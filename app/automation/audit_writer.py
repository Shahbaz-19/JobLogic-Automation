import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUDIT_COLUMNS = [
    "Timestamp",
    "RowNumber",
    "CustomerName",
    "SiteName",
    "CustomerExternalId",
    "SiteExternalId",
    "JobExternalId",
    "Status",
    "CustomerAction",
    "SiteAction",
    "JobAction",
    "MissingFields",
    "PartialFields",
    "TagWarning",
    "Error",
]


def get_daily_audit_filename() -> Path:
    """Return default daily audit file path formatted as audit/audit_YYYY-MM-DD.csv."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return Path(f"audit/audit_{date_str}.csv")


class AuditWriter:
    """
    Writes one audit record for every processed Excel row.

    Defaults to a daily date-stamped file in the audit/ directory
    (e.g., audit/audit_YYYY-MM-DD.csv) with append-safe initialization
    so that each day's 9 hourly executions accumulate cleanly in that day's file.
    """

    def __init__(
        self,
        file_path: str | Path | None = None,
    ) -> None:
        if file_path is None:
            self.file_path = get_daily_audit_filename()
        else:
            self.file_path = Path(file_path)

    def initialize(self) -> None:
        """
        Create the audit file and its parent directory with headers if it does not exist.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if self.file_path.exists() and self.file_path.stat().st_size > 0:
            return

        self._write_header()

    def reset(self) -> None:
        """
        Start a completely fresh audit file, overwriting any previous content.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_header()

    def _write_header(self) -> None:
        """
        Create the audit file and write its header.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open(
            mode="w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=AUDIT_COLUMNS,
            )
            writer.writeheader()

    def write_row(
        self,
        row_number: int,
        source_row: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        """
        Write one processed Excel row to the audit file.
        """
        self.initialize()

        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        audit_record = {
            "Timestamp": timestamp_str,
            "RowNumber": row_number,
            "CustomerName": source_row.get(
                "Customer Name",
                "",
            ),
            "SiteName": source_row.get(
                "Site Name",
                "",
            ),
            "CustomerExternalId": result.get(
                "customer_external_id",
                "",
            ),
            "SiteExternalId": result.get(
                "site_external_id",
                "",
            ),
            "JobExternalId": result.get(
                "job_external_id",
                "",
            ),
            "Status": result.get(
                "status",
                "",
            ),
            "CustomerAction": result.get(
                "customer_action",
                "",
            ),
            "SiteAction": result.get(
                "site_action",
                "",
            ),
            "JobAction": result.get(
                "job_action",
                "",
            ),
            "MissingFields": result.get(
                "missing_fields",
                "",
            ),
            "PartialFields": result.get(
                "partial_fields",
                "",
            ),
            "TagWarning": result.get(
                "tag_warning",
                "",
            ),
            "Error": result.get(
                "error",
                "",
            ),
        }

        with self.file_path.open(
            mode="a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=AUDIT_COLUMNS,
            )
            writer.writerow(audit_record)