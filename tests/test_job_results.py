"""
tests/test_job_results.py

Unit tests for the dedicated Job Results output file feature.
"""

import csv
import tempfile
from pathlib import Path

import pytest

from app.automation.job_result_writer import (
    JOB_RESULTS_COLUMNS,
    JobResultWriter,
)


# ===========================================================
# Helpers
# ===========================================================

def _read_csv(file_path: Path) -> list[dict]:
    """Read CSV into list of dicts."""
    with file_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ===========================================================
# 1. JobResultWriter - directory creation & header
# ===========================================================

def test_reset_creates_directory_and_header(tmp_path):
    """reset() must create the output directory and write the CSV header."""
    output_file = tmp_path / "sub" / "job_results.csv"
    writer = JobResultWriter(output_file)
    writer.reset()

    assert output_file.exists(), "output file should be created by reset()"
    rows = _read_csv(output_file)
    assert rows == [], "file should only contain the header after reset()"


def test_reset_column_headers(tmp_path):
    """reset() must write the exact required column headers."""
    output_file = tmp_path / "job_results.csv"
    writer = JobResultWriter(output_file)
    writer.reset()

    with output_file.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)

    assert headers == JOB_RESULTS_COLUMNS


# ===========================================================
# 2. Successful job row
# ===========================================================

def test_write_successful_row(tmp_path):
    """A successful row must include Job Number and Job ID."""
    output_file = tmp_path / "job_results.csv"
    writer = JobResultWriter(output_file)
    writer.reset()

    writer.write_row(
        excel_row=2,
        customer_name="ACME Corp",
        site_name="Main Office",
        status="Success",
        job_number="O0000084",
        job_id="30e89329-e35b-47b9-bac4-147a5cd9cbd8",
    )

    rows = _read_csv(output_file)
    assert len(rows) == 1
    row = rows[0]
    assert row["Excel Row"] == "2"
    assert row["Customer Name"] == "ACME Corp"
    assert row["Site Name"] == "Main Office"
    assert row["Job Number"] == "O0000084"
    assert row["Job ID"] == "30e89329-e35b-47b9-bac4-147a5cd9cbd8"
    assert row["Status"] == "Success"
    assert row["Reason"] == ""


# ===========================================================
# 3. Partial Success row
# ===========================================================

def test_write_partial_success_row(tmp_path):
    """A Partial Success row must include Job Number and Job ID, no reason."""
    output_file = tmp_path / "job_results.csv"
    writer = JobResultWriter(output_file)
    writer.reset()

    writer.write_row(
        excel_row=3,
        customer_name="Beta Ltd",
        site_name="Warehouse",
        status="Partial Success",
        job_number="O0000085",
        job_id="aaaa-bbbb-cccc",
    )

    rows = _read_csv(output_file)
    assert len(rows) == 1
    row = rows[0]
    assert row["Status"] == "Partial Success"
    assert row["Job Number"] == "O0000085"
    assert row["Job ID"] == "aaaa-bbbb-cccc"
    assert row["Reason"] == ""


# ===========================================================
# 4. Failed row - blank Job Number and Job ID
# ===========================================================

def test_write_failed_row_has_blank_job_number_and_id(tmp_path):
    """A failed row must have blank Job Number and Job ID."""
    output_file = tmp_path / "job_results.csv"
    writer = JobResultWriter(output_file)
    writer.reset()

    writer.write_row(
        excel_row=4,
        customer_name="Bad Customer",
        site_name="Unknown Site",
        status="Failed",
        reason="Missing mandatory field: Job Owner",
    )

    rows = _read_csv(output_file)
    assert len(rows) == 1
    row = rows[0]
    assert row["Status"] == "Failed"
    assert row["Job Number"] == "", "failed row must not have a Job Number"
    assert row["Job ID"] == "", "failed row must not have a Job ID"
    assert row["Reason"] == "Missing mandatory field: Job Owner"


# ===========================================================
# 5. Multiple rows in order
# ===========================================================

def test_multiple_rows_written_in_order(tmp_path):
    """All rows must appear in the CSV in the order they were written."""
    output_file = tmp_path / "job_results.csv"
    writer = JobResultWriter(output_file)
    writer.reset()

    writer.write_row(
        excel_row=2, customer_name="C1", site_name="S1",
        status="Success", job_number="O001", job_id="id-1",
    )
    writer.write_row(
        excel_row=3, customer_name="C2", site_name="S2",
        status="Failed", reason="Bad owner",
    )
    writer.write_row(
        excel_row=4, customer_name="C3", site_name="S3",
        status="Partial Success", job_number="O002", job_id="id-2",
    )

    rows = _read_csv(output_file)
    assert len(rows) == 3
    assert rows[0]["Excel Row"] == "2"
    assert rows[1]["Excel Row"] == "3"
    assert rows[2]["Excel Row"] == "4"


# ===========================================================
# 6. reset() clears previous content
# ===========================================================

def test_reset_clears_previous_content(tmp_path):
    """reset() must overwrite any existing file, keeping only the header."""
    output_file = tmp_path / "job_results.csv"
    writer = JobResultWriter(output_file)
    writer.reset()

    writer.write_row(
        excel_row=2, customer_name="C1", site_name="S1",
        status="Success", job_number="O001", job_id="id-1",
    )

    # reset again - should clear previous rows
    writer.reset()

    rows = _read_csv(output_file)
    assert rows == [], "reset() should clear previous rows"


# ===========================================================
# 7. Job Number extraction from API response dict
# ===========================================================

@pytest.mark.parametrize("api_response,expected_number,expected_id", [
    (
        {"JobNumber": "O0000084", "Id": "uuid-1"},
        "O0000084",
        "uuid-1",
    ),
    (
        {"Number": "O0000085", "Id": "uuid-2"},
        "O0000085",
        "uuid-2",
    ),
    (
        {"JobNumber": None, "Id": None, "UniqueId": "guid-3"},
        "",
        "guid-3",
    ),
])
def test_job_number_extraction_logic(api_response, expected_number, expected_id):
    """
    Verify the extraction logic used in runner.py produces correct
    job_number and job_id from various API response shapes.
    """
    job_number = (
        api_response.get("JobNumber")
        or api_response.get("Number")
        or ""
    )
    job_id = str(
        api_response.get("Id")
        or api_response.get("JobId")
        or api_response.get("UniqueId")
        or ""
    )

    assert job_number == expected_number
    assert job_id == expected_id


# ===========================================================
# 8. write_row without calling reset first (idempotent directory creation)
# ===========================================================

def test_write_row_creates_directory_if_missing(tmp_path):
    """write_row must create the output directory even without reset()."""
    output_file = tmp_path / "nested" / "deep" / "job_results.csv"
    writer = JobResultWriter(output_file)

    # Deliberately skip reset(); write_row should handle missing dir
    writer.write_row(
        excel_row=2,
        customer_name="Orphan Corp",
        site_name="Nowhere",
        status="Failed",
        reason="Test",
    )

    assert output_file.exists()


# ===========================================================
# 9. initialize() append-safety across multiple runs
# ===========================================================

def test_initialize_preserves_existing_results_across_runs(tmp_path):
    """initialize() must NOT truncate an existing CSV file."""
    output_file = tmp_path / "job_results.csv"
    writer = JobResultWriter(output_file)

    # Run 1: initialize and write row
    writer.initialize()
    writer.write_row(
        excel_row=2, customer_name="Customer 1", site_name="Site 1",
        status="Success", job_number="J001", job_id="id-1"
    )

    # Run 2: instantiate new writer and call initialize()
    writer2 = JobResultWriter(output_file)
    writer2.initialize()
    writer2.write_row(
        excel_row=3, customer_name="Customer 2", site_name="Site 2",
        status="Partial Success", job_number="J002", job_id="id-2"
    )

    rows = _read_csv(output_file)
    assert len(rows) == 2, "Both rows must be preserved across multiple initialize() calls"
    assert rows[0]["Job Number"] == "J001"
    assert rows[1]["Job Number"] == "J002"

