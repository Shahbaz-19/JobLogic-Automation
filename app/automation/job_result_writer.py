import csv
from pathlib import Path

JOB_RESULTS_COLUMNS = [
    "Excel Row",
    "Customer Name",
    "Site Name",
    "Job Number",
    "Job ID",
    "Status",
    "Reason",
]


class JobResultWriter:
    """
    Appends per-row JobLogic automation results to a dedicated CSV file.

    Existing results are preserved across automation runs.
    Actual Job Number and Job ID returned by the JobLogic API are stored.
    """

    def __init__(self, file_path: str | Path = "output/job_results.csv") -> None:
        self.file_path = Path(file_path).resolve()

    def initialize(self) -> None:
        """
        Create the output directory and CSV header only when the file
        does not already exist or is empty.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            with self.file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(JOB_RESULTS_COLUMNS)

    def reset(self) -> None:
        """
        Overwrite any existing file and create a fresh CSV with only headers.
        """
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(JOB_RESULTS_COLUMNS)

    def write_row(
        self,
        excel_row: int,
        customer_name: str,
        site_name: str,
        status: str,
        job_number: str | None = None,
        job_id: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Append one row to the existing job results CSV file."""

        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Make sure the header exists without deleting previous results.
        self.initialize()

        row_data = [
            excel_row,
            customer_name or "",
            site_name or "",
            job_number or "",
            job_id or "",
            status or "",
            reason or "",
        ]

        with self.file_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row_data)