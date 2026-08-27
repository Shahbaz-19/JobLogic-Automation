from datetime import datetime, timezone
import hashlib
import json
import logging
import unicodedata
from pathlib import Path
from typing import Any

from app.automation.audit_writer import AuditWriter
from app.automation.excel_reader import read_excel_file
from app.automation.job_result_writer import JobResultWriter
from app.automation.processor import JobProcessor
from app.automation.resolver import Resolver
from app.clients.joblogic_client import JoblogicClient
from app.config import Settings
from app.joblogic.jobs.service import JobService

logger = logging.getLogger(__name__)


class AutomationRunner:
    """
    Runs the complete Excel -> JobLogic automation.

    Each Excel row is processed independently.

    A failure in one row does not stop the remaining rows.
    """

    def __init__(
        self,
        settings: Settings,
        client: JoblogicClient,
        audit_file: str | Path | None = None,
        job_results_file: str = "output/job_results.csv",
    ) -> None:

        self._settings = settings
        self._client = client

        self._resolver = Resolver(
            settings,
            client,
        )

        self._processor = JobProcessor(
            settings,
            client,
        )

        self._job_service = JobService(
            settings,
            client,
        )

        self._audit_writer = AuditWriter(
            audit_file,
        )

        self._job_result_writer = JobResultWriter(
            job_results_file,
        )

    def resolve_input_file(
        self,
        excel_file: str | Path | None = None,
    ) -> Path:
        """
        Determine which Excel file to process based on priority:
        1. Explicitly passed excel_file argument
        2. settings.excel_input_file
        Fails if neither is configured or if the file does not exist.
        """
        selected: str | Path | None = excel_file or self._settings.excel_input_file

        if not selected or not str(selected).strip():
            raise ValueError(
                "Excel input file not specified. Provide an input path via CLI (--input) or set EXCEL_INPUT_FILE in environment/configuration."
            )

        resolved_path = Path(str(selected).strip()).resolve()

        if not resolved_path.exists():
            raise FileNotFoundError(
                f"Input Excel file not found: {resolved_path}"
            )

        return resolved_path

    async def run(
        self,
        excel_file: str | Path | None = None,
    ) -> None:

        # ========================================================
        # 1. RESOLVE & READ EXCEL
        # ========================================================

        target_file = self.resolve_input_file(excel_file)

        # Initialise the job results output file
        self._job_result_writer.initialize()

        output_results_path = self._job_result_writer.file_path
        audit_path = self._audit_writer.file_path
        logger.info("Input Excel file: %s", target_file)
        logger.info("Output results file: %s", output_results_path)
        logger.info("Audit file: %s", audit_path)
        print(f"Input Excel file: {target_file}")
        print(f"Output results file: {output_results_path}")
        print(f"Audit file: {audit_path}")

        rows = read_excel_file(
            target_file
        )

        logger.info("Number of rows loaded: %d", len(rows))
        print(f"Number of rows loaded: {len(rows)}")

        # ========================================================
        # 2. INITIALIZE AUDIT FILE
        # ========================================================

        self._audit_writer.initialize()

        # ========================================================
        # 3. GET TENANT ID
        # ========================================================

        if self._settings.joblogic_tenant_id is None:
            raise RuntimeError(
                "JOBLOGIC_TENANT_ID is not configured."
            )

        tenant_id = str(
            self._settings.joblogic_tenant_id
        )

        # ========================================================
        # 4. PRE-CHECK TAGS
        # ========================================================

        # Verify that both outcome tags exist in Joblogic before
        # processing any rows. This is a once-per-run lookup.
        # If a tag is not found we log a warning but still send
        # the tag name in the job payload — Joblogic may auto-
        # create it, or it may be silently dropped. Both outcomes
        # must be confirmed in UAT.

        verified_tags = await self._verify_tags(
            tenant_id=tenant_id,
        )

        for tag_name, found in verified_tags.items():
            if found:
                print(
                    f"Tag pre-check: \"{tag_name}\" "
                    f"found in Joblogic [OK]"
                )
            else:
                print(
                    f"Tag pre-check WARNING: "
                    f"\"{tag_name}\" not found in "
                    f"Joblogic — will still be sent "
                    f"in job payload (behaviour "
                    f"unconfirmed)."
                )

        # ========================================================
        # 5. PROCESS EVERY ROW  (per-run counters)
        # ========================================================

        count_success = 0
        count_partial = 0
        count_failed = 0
        count_created = 0

        for index, row in enumerate(
            rows,
            start=2,
        ):

            print(
                f"\nProcessing Excel row {index}..."
            )

            try:

                # ------------------------------------------------
                # Generate deterministic External IDs
                # ------------------------------------------------

                customer_external_id = (
                    self._generate_external_id(
                        "customer",
                        row,
                    )
                )

                site_external_id = (
                    self._generate_external_id(
                        "site",
                        row,
                    )
                )

                job_external_id = (
                    self._generate_external_id(
                        "job",
                        row,
                    )
                )

                print(
                    f"Customer External ID: "
                    f"{customer_external_id}"
                )

                print(
                    f"Site External ID: "
                    f"{site_external_id}"
                )

                print(
                    f"Job External ID: "
                    f"{job_external_id}"
                )

                # ------------------------------------------------
                # Process row
                # ------------------------------------------------

                result = (
                    await self._processor.process_row(
                        row=row,
                        tenant_id=tenant_id,
                        customer_external_id=(
                            customer_external_id
                        ),
                        site_external_id=(
                            site_external_id
                        ),
                        job_external_id=(
                            job_external_id
                        ),
                        verified_tags=verified_tags,
                    )
                )

                customer_name = str(
                    row.get("Customer Name", "")
                    or ""
                ).strip()
                site_name = str(
                    row.get("Site Name", "")
                    or ""
                ).strip()

                # ------------------------------------------------
                # Processor failure
                # ------------------------------------------------

                if result.get("status") == "Failed":

                    reason = (
                        result.get("error")
                        or result.get("missing_fields")
                        or "Unknown failure"
                    )

                    print(
                        f"\nJob creation failed"
                        f"\nExcel Row: {index}"
                        f"\nCustomer: {customer_name}"
                        f"\nSite: {site_name}"
                        f"\nReason: {reason}"
                    )

                    self._job_result_writer.write_row(
                        excel_row=index,
                        customer_name=customer_name,
                        site_name=site_name,
                        status="Failed",
                        reason=reason,
                    )

                    self._audit_writer.write_row(
                        row_number=index,
                        source_row=row,
                        result=result,
                    )

                    count_failed += 1
                    continue

                # ------------------------------------------------
                # Get prepared Job payload
                # ------------------------------------------------

                job_payload = result.get(
                    "job_payload"
                )

                if not job_payload:

                    result["status"] = "Failed"

                    result["job_action"] = (
                        "Not Created"
                    )

                    result["error"] = (
                        "Processor did not return "
                        "a job payload"
                    )

                    reason = result["error"]

                    print(
                        f"\nJob creation failed"
                        f"\nExcel Row: {index}"
                        f"\nCustomer: {customer_name}"
                        f"\nSite: {site_name}"
                        f"\nReason: {reason}"
                    )

                    self._job_result_writer.write_row(
                        excel_row=index,
                        customer_name=customer_name,
                        site_name=site_name,
                        status="Failed",
                        reason=reason,
                    )

                    self._audit_writer.write_row(
                        row_number=index,
                        source_row=row,
                        result=result,
                    )

                    count_failed += 1
                    continue

                # ------------------------------------------------
                # CREATE JOB
                # ------------------------------------------------

                try:

                    created_job = (
                        await self._job_service.create_job(
                            job_payload
                        )
                    )

                    result["job_action"] = (
                        "Created"
                    )

                    if result.get(
                        "partial_fields"
                    ):
                        result["status"] = (
                            "Partial Success"
                        )
                    else:
                        result["status"] = (
                            "Success"
                        )

                    # Extract Job Number and Job ID
                    # from actual API response
                    job_number = (
                        created_job.get("JobNumber")
                        or created_job.get("Number")
                        or ""
                    )
                    job_id = str(
                        created_job.get("Id")
                        or created_job.get("JobId")
                        or created_job.get("UniqueId")
                        or ""
                    )

                    print(
                        f"\nJob created successfully"
                        f"\nExcel Row: {index}"
                        f"\nCustomer: {customer_name}"
                        f"\nSite: {site_name}"
                        f"\nJob Number: {job_number}"
                        f"\nJob ID: {job_id}"
                    )

                    # JobLogic stores Job Notes through POST /api/v1/Note.
                    # EntityId must be the ID returned by Create Job.
                    note_text = str(row.get("Notes") or "").strip()
                    if note_text:
                        if not job_id:
                            result["status"] = "Partial Success"
                            result["error"] = (
                                "Job created successfully, but Job ID was not "
                                "returned; Job Note could not be created"
                            )
                            print(f"Job Note creation failed: {result['error']}")
                        else:
                            note_payload = {
                                "EntityId": job_id,
                                "EntityType": 3,
                                "NoteText": note_text,
                                "DateAdded": datetime.now(timezone.utc).isoformat(
                                    timespec="milliseconds"
                                ).replace("+00:00", "Z"),
                                "IsPrivate": False,
                                "Attachments": [],
                                "Tags": [],
                                "IsPrivateAndShowOnMobile": False,
                                "TenantId": tenant_id,
                            }
                            try:
                                await self._job_service.create_note(note_payload)
                                print("Job Note created successfully")
                            except Exception as note_exc:
                                result["status"] = "Partial Success"
                                result["error"] = (
                                    "Job created successfully, but Job Note creation failed: "
                                    f"{note_exc}"
                                )
                                print(f"Job Note creation failed: {note_exc}")

                    reason = result.get("error", "")

                    self._job_result_writer.write_row(
                        excel_row=index,
                        customer_name=customer_name,
                        site_name=site_name,
                        status=result["status"],
                        job_number=job_number,
                        job_id=job_id,
                        reason=reason or None,
                    )

                    count_created += 1
                    if result["status"] == "Success":
                        count_success += 1
                    else:
                        count_partial += 1

                except Exception as exc:

                    result["status"] = "Failed"

                    result["job_action"] = (
                        "Not Created"
                    )

                    result["error"] = (
                        f"Job creation failed: {exc}"
                    )

                    reason = result["error"]

                    print(
                        f"\nJob creation failed"
                        f"\nExcel Row: {index}"
                        f"\nCustomer: {customer_name}"
                        f"\nSite: {site_name}"
                        f"\nReason: {reason}"
                    )

                    self._job_result_writer.write_row(
                        excel_row=index,
                        customer_name=customer_name,
                        site_name=site_name,
                        status="Failed",
                        reason=reason,
                    )

                    count_failed += 1

                # ------------------------------------------------
                # WRITE AUDIT
                # ------------------------------------------------

                self._audit_writer.write_row(
                    row_number=index,
                    source_row=row,
                    result=result,
                )

            except Exception as exc:

                # ------------------------------------------------
                # Unexpected row-level failure
                # ------------------------------------------------

                result = {
                    "status": "Failed",
                    "customer_action": "",
                    "site_action": "",
                    "job_action": "Not Created",
                    "missing_fields": "",
                    "partial_fields": "",
                    "error": str(exc),
                }

                customer_name = str(
                    row.get("Customer Name", "") or ""
                ).strip()
                site_name = str(
                    row.get("Site Name", "") or ""
                ).strip()
                reason = str(exc)

                print(
                    f"\nJob creation failed"
                    f"\nExcel Row: {index}"
                    f"\nCustomer: {customer_name}"
                    f"\nSite: {site_name}"
                    f"\nReason: {reason}"
                )

                self._job_result_writer.write_row(
                    excel_row=index,
                    customer_name=customer_name,
                    site_name=site_name,
                    status="Failed",
                    reason=reason,
                )

                self._audit_writer.write_row(
                    row_number=index,
                    source_row=row,
                    result=result,
                )

                count_failed += 1

        # ========================================================
        # 6. SUMMARY
        # ========================================================

        rows_processed = len(rows)
        print(
            f"\nAutomation completed."
            f"\n"
            f"\nRows processed: {rows_processed}"
            f"\nJobs created: {count_created}"
            f"\nSuccessful: {count_success}"
            f"\nPartial Success: {count_partial}"
            f"\nFailed: {count_failed}"
            f"\n"
            f"\nJob results file: {output_results_path}"
        )

    # ============================================================
    # TAG VERIFICATION
    # ============================================================

    async def _verify_tags(
        self,
        tenant_id: str,
    ) -> dict[str, bool]:
        """
        Check whether the two outcome tags exist in Joblogic.

        Called once per run, before the row loop.

        Returns a mapping of {tag_name: found} so every row can
        record a TagWarning in the audit file when a tag was not
        confirmed to exist.

        Tags that are not found are still sent in the job payload;
        whether Joblogic auto-creates or silently drops unknown
        tag strings has not yet been confirmed in UAT.
        """

        tag_names = ["Success", "Partial Success"]

        results: dict[str, bool] = {}

        for tag_name in tag_names:
            tag = await self._resolver.find_tag(
                tag_name=tag_name,
                tenant_id=tenant_id,
            )
            results[tag_name] = tag is not None

        return results

    # ============================================================
    # EXTERNAL ID GENERATION
    # ============================================================

    @staticmethod
    def _generate_external_id(
        entity_type: str,
        row: dict[str, Any],
    ) -> str:

        # --------------------------------------------------------
        # Customer
        # --------------------------------------------------------

        if entity_type == "customer":

            customer = AutomationRunner._normalise(
                row.get(
                    "Customer Name",
                    "",
                )
            )

            canonical = (
                f"v1|customer|{customer}"
            )

            prefix = "JLA-C-"

        # --------------------------------------------------------
        # Site
        # --------------------------------------------------------

        elif entity_type == "site":

            customer = AutomationRunner._normalise(
                row.get(
                    "Customer Name",
                    "",
                )
            )

            site = AutomationRunner._normalise(
                row.get(
                    "Site Name",
                    "",
                )
            )

            canonical = (
                f"v1|site|{customer}|{site}"
            )

            prefix = "JLA-S-"

        # --------------------------------------------------------
        # Job
        # --------------------------------------------------------

        elif entity_type == "job":

            customer = AutomationRunner._normalise(
                row.get(
                    "Customer Name",
                    "",
                )
            )

            site = AutomationRunner._normalise(
                row.get(
                    "Site Name",
                    "",
                )
            )

            fields = [
                "Customer Name",
                "Site Name",
                "Job Description",
                "Job Type",
                "Job Owner",
                "Job Priority",
                "Job Category",
                "Primary Job Trade",
                "Order Number",
                "Ref Number",
                "Notes",
            ]

            values = []

            for field in fields:

                value = row.get(field)

                if value is None:
                    value = None

                elif str(value).strip() == "":
                    value = None

                else:
                    value = AutomationRunner._normalise(
                        value
                    )

                values.append(value)

            canonical_values = json.dumps(
                values,
                ensure_ascii=False,
                separators=(",", ":"),
            )

            canonical = (
                f"v1|job|"
                f"{customer}|"
                f"{site}|"
                f"{canonical_values}"
            )

            prefix = "JLA-J-"

        else:

            raise ValueError(
                f"Unsupported entity type: {entity_type}"
            )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()[:32]

        return f"{prefix}{digest}"

    # ============================================================
    # NORMALISATION
    # ============================================================

    @staticmethod
    def _normalise(
        value: Any,
    ) -> str:

        value = unicodedata.normalize(
            "NFC",
            str(value),
        )

        value = " ".join(
            value.strip().split()
        )

        return value.casefold()