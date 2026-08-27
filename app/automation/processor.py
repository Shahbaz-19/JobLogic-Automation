from datetime import datetime, timezone
from typing import Any

from app.automation.resolver import Resolver, ResolutionError
from app.clients.joblogic_client import JoblogicClient
from app.config import Settings


MANDATORY_FIELDS = [
    "Customer Name",
    "Site Name",
    "Job Description",
    "Job Type",
    "Job Owner",
]


class JobProcessor:
    """
    Processes one Excel row and prepares the JobLogic Job payload.

    Required (row fails if any are missing or cannot be resolved):
        Customer Name
        Site Name
        Job Description
        Job Type
        Job Owner

    Optional (blank or invalid → Partial Success, not Failed):
        Job Priority
        Job Category
        Primary Job Trade
        Order Number
        Ref Number
        Notes
    """

    def __init__(
        self,
        settings: Settings,
        client: JoblogicClient,
    ) -> None:
        self._settings = settings
        self._client = client
        self._resolver = Resolver(settings, client)

    async def process_row(
        self,
        row: dict[str, Any],
        tenant_id: str,
        customer_external_id: str,
        site_external_id: str,
        job_external_id: str,
        verified_tags: dict[str, bool] | None = None,
    ) -> dict[str, Any]:

        # ========================================================
        # 1. VALIDATE MANDATORY FIELDS
        # ========================================================

        missing_fields = [
            field
            for field in MANDATORY_FIELDS
            if self._is_empty(row.get(field))
        ]

        if missing_fields:
            if "Job Owner" in missing_fields and len(missing_fields) == 1:
                err_msg = "Job Owner is required"
            else:
                err_msg = f"Mandatory field(s) missing: {', '.join(missing_fields)}"

            return {
                "status": "Failed",
                "customer_action": "",
                "site_action": "",
                "job_action": "Not Created",
                "missing_fields": ", ".join(missing_fields),
                "partial_fields": "",
                "tag_warning": "",
                "error": err_msg,
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        customer_name = str(
            row["Customer Name"]
        ).strip()

        site_name = str(
            row["Site Name"]
        ).strip()

        description = str(
            row["Job Description"]
        ).strip()

        job_type = str(
            row["Job Type"]
        ).strip()

        job_owner_name = str(
            row["Job Owner"]
        ).strip()

        # ========================================================
        # 2. RESOLVE CUSTOMER
        # ========================================================

        try:
            customer, customer_action = (
                await self._resolver.resolve_customer(
                    customer_name=customer_name,
                    external_id=customer_external_id,
                    tenant_id=tenant_id,
                )
            )

        except Exception as exc:
            return {
                "status": "Failed",
                "customer_action": "Error",
                "site_action": "",
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": f"Customer resolution failed: {exc}",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        # ========================================================
        # 3. GET CUSTOMER ID
        # ========================================================

        customer_id = customer.get("Id")

        if customer_id is None:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": "",
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": "Customer response did not contain Id",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        customer_guid = (
            customer.get("UniqueId")
            or customer.get("Id")
        )

        # ========================================================
        # 4. RESOLVE SITE
        # ========================================================

        try:
            site, site_action = (
                await self._resolver.resolve_site(
                    site_name=site_name,
                    customer_id=customer_id,
                    customer_guid=str(customer_guid),
                    external_id=site_external_id,
                    tenant_id=tenant_id,
                )
            )

        except Exception as exc:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": "Error",
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": f"Site resolution failed: {exc}",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        site_id = site.get("Id")

        if site_id is None:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": site_action,
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": "Site response did not contain Id",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        # ========================================================
        # 5. RESOLVE JOB TYPE (MANDATORY)
        # ========================================================

        try:
            job_type_result = (
                await self._resolver.find_job_type(
                    value=job_type,
                    tenant_id=tenant_id,
                )
            )

        except Exception as exc:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": site_action,
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": f"Job Type resolution failed: {exc}",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        if job_type_result is None:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": site_action,
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": f"Job Type not found: {job_type}",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        # ========================================================
        # 6. RESOLVE JOB OWNER (MANDATORY)
        # ========================================================

        try:
            job_owner_result = (
                await self._resolver.find_staff(
                    value=job_owner_name,
                    tenant_id=tenant_id,
                )
            )

        except ResolutionError as exc:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": site_action,
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": str(exc),
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        except Exception as exc:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": site_action,
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": f"Job Owner resolution failed: {exc}",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        if job_owner_result is None or job_owner_result.get("IntId") is None:
            return {
                "status": "Failed",
                "customer_action": customer_action,
                "site_action": site_action,
                "job_action": "Not Created",
                "missing_fields": "",
                "partial_fields": "",
                "tag_warning": "",
                "error": f"Job Owner not found: {job_owner_name}",
                "customer_external_id": customer_external_id,
                "site_external_id": site_external_id,
                "job_external_id": job_external_id,
            }

        # ========================================================
        # 7. RESOLVE OPTIONAL FIELDS
        # ========================================================

        partial_fields: list[str] = []

        job_priority = await self._resolve_optional(
            row.get("Job Priority"),
            self._resolver.find_priority,
            tenant_id,
            "Job Priority",
            partial_fields,
        )

        job_category = await self._resolve_optional(
            row.get("Job Category"),
            self._resolver.find_job_category,
            tenant_id,
            "Job Category",
            partial_fields,
        )

        primary_trade = await self._resolve_optional(
            row.get("Primary Job Trade"),
            self._resolver.find_trade,
            tenant_id,
            "Primary Job Trade",
            partial_fields,
        )

        # Track blank optional text fields
        if self._is_empty(row.get("Order Number")):
            partial_fields.append("Order Number")

        if self._is_empty(row.get("Ref Number")):
            partial_fields.append("Ref Number")

        if self._is_empty(row.get("Notes")):
            partial_fields.append("Notes")

        # ========================================================
        # 8. BUILD JOB PAYLOAD
        # ========================================================

        job_payload: dict[str, Any] = {
            "ExternalId": job_external_id,
            "Customer": {
                "Id": customer.get("UniqueId")
                or customer.get("Id"),
            },
            "Site": {
                "Id": site.get("UniqueId")
                or site.get("Id"),
            },
            "Description": description,
            "JobType": job_type_result.get(
                "Description",
                job_type,
            ),
            "DateLogged": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "Status": "New Job",
            "TenantId": tenant_id,
        }

        # ========================================================
        # 9. OPTIONAL PLAIN-TEXT FIELDS
        # ========================================================

        if not self._is_empty(
            row.get("Order Number")
        ):
            job_payload["OrderNumber"] = str(
                row["Order Number"]
            ).strip()

        if not self._is_empty(
            row.get("Ref Number")
        ):
            job_payload["ReferenceNumber"] = str(
                row["Ref Number"]
            ).strip()

        # JobLogic stores Job Notes through POST /api/v1/Note after the
        # Job has been created.  Do not put Notes into the Create Job
        # payload; the runner creates the Note using the returned Job ID.

        # ========================================================
        # 10. OPTIONAL RESOLVED VALUES
        # ========================================================

        if job_priority:
            job_payload["PriorityLevel"] = (
                job_priority.get("Description")
            )

        if job_category:
            job_payload["JobCategory"] = (
                job_category.get("Description")
            )

        # AdditionalDetail carries Trade and OwnerUserId (if integer)
        additional_detail: dict[str, Any] = {}

        if primary_trade:
            additional_detail["Trade"] = (
                primary_trade.get("Description")
            )

        owner_user_id = None
        for key in ("UserId", "OwnerUserId", "Id", "StaffId"):
            val = job_owner_result.get(key)
            if val is not None:
                try:
                    owner_user_id = int(val)
                    break
                except (ValueError, TypeError):
                    continue

        if owner_user_id is not None:
            additional_detail["OwnerUserId"] = owner_user_id

        if additional_detail:
            job_payload["AdditionalDetail"] = additional_detail

        # ========================================================
        # 11. TAGS — "Success" or "Partial Success"
        # ========================================================

        # Tags reflect the final row outcome:
        #   "Success"         → all mandatory AND optional fields resolved
        #   "Partial Success" → mandatory fields ok; ≥1 optional field
        #                       was empty or not found in Joblogic
        #
        # If the tag was not found during the pre-run check (Tag/GetAll),
        # a warning is recorded in the audit record, but the tag name is
        # still sent in the job payload (Joblogic may auto-create it).

        tag_name = "Partial Success" if partial_fields else "Success"
        job_payload["Tags"] = [tag_name]

        tag_warning = ""
        if verified_tags is not None and not verified_tags.get(tag_name, True):
            tag_warning = (
                f"Tag '{tag_name}' not found in Joblogic (sent in payload)"
            )

        # ========================================================
        # 12. RETURN RESULT
        # ========================================================

        return {
            "status": (
                "Partial Success"
                if partial_fields
                else "Success"
            ),
            "customer_action": customer_action,
            "site_action": site_action,
            "job_action": "Ready",
            "missing_fields": "",
            "partial_fields": ", ".join(
                partial_fields
            ),
            "tag_warning": tag_warning,
            "error": "",
            "customer_external_id": customer_external_id,
            "site_external_id": site_external_id,
            "job_external_id": job_external_id,
            "job_payload": job_payload,
        }

    async def _resolve_optional(
        self,
        value: Any,
        resolver_method: Any,
        tenant_id: str,
        field_name: str,
        partial_fields: list[str],
    ) -> dict[str, Any] | None:

        if self._is_empty(value):
            partial_fields.append(field_name)
            return None

        try:
            result = await resolver_method(
                value=str(value).strip(),
                tenant_id=tenant_id,
            )
        except Exception:
            partial_fields.append(field_name)
            return None

        if result is None:
            partial_fields.append(field_name)
            return None

        return result

    @staticmethod
    def _is_empty(
        value: Any,
    ) -> bool:

        if value is None:
            return True

        if isinstance(value, str):
            return not value.strip()

        return False