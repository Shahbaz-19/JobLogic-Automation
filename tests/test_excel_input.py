import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd

from app.automation.excel_reader import read_excel_file
from app.automation.runner import AutomationRunner
from app.config import Settings


@pytest.fixture
def temp_excel_file_a(tmp_path):
    file_path = tmp_path / "file_a.xlsx"
    df = pd.DataFrame([
        {
            "Customer Name": "Customer A",
            "Site Name": "Site A",
            "Job Description": "Desc A",
            "Job Type": "Callout",
            "Job Owner": "Owner A",
        }
    ])
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def temp_excel_file_b(tmp_path):
    file_path = tmp_path / "file_b.xlsx"
    df = pd.DataFrame([
        {
            "Customer Name": "Customer B1",
            "Site Name": "Site B1",
            "Job Description": "Desc B1",
            "Job Type": "Callout",
            "Job Owner": "Owner B1",
        },
        {
            "Customer Name": "Customer B2",
            "Site Name": "Site B2",
            "Job Description": "Desc B2",
            "Job Type": "Callout",
            "Job Owner": "Owner B2",
        }
    ])
    df.to_excel(file_path, index=False)
    return file_path


def test_resolve_input_file_explicit_cli(temp_excel_file_a, temp_excel_file_b):
    settings = Settings(
        excel_input_file=str(temp_excel_file_b),
        joblogic_tenant_id="00000000-0000-0000-0000-000000000001",
    )
    runner = AutomationRunner(settings=settings, client=MagicMock())

    resolved = runner.resolve_input_file(excel_file=str(temp_excel_file_a))
    assert resolved == temp_excel_file_a.resolve()


def test_resolve_input_file_from_settings(temp_excel_file_b):
    settings = Settings(
        excel_input_file=str(temp_excel_file_b),
        joblogic_tenant_id="00000000-0000-0000-0000-000000000001",
    )
    runner = AutomationRunner(settings=settings, client=MagicMock())

    resolved = runner.resolve_input_file(excel_file=None)
    assert resolved == temp_excel_file_b.resolve()


def test_resolve_input_file_missing_file_raises():
    settings = Settings(
        excel_input_file="TestAutomation/non_existent_file.xlsx",
        joblogic_tenant_id="00000000-0000-0000-0000-000000000001",
    )
    runner = AutomationRunner(settings=settings, client=MagicMock())

    with pytest.raises(FileNotFoundError, match="Input Excel file not found"):
        runner.resolve_input_file(excel_file=None)


def test_resolve_input_file_neither_configured_raises():
    settings = Settings(
        excel_input_file=None,
        joblogic_tenant_id="00000000-0000-0000-0000-000000000001",
    )
    runner = AutomationRunner(settings=settings, client=MagicMock())

    with pytest.raises(ValueError, match="Excel input file not specified"):
        runner.resolve_input_file(excel_file=None)


def test_read_excel_file_loads_correct_rows(temp_excel_file_a, temp_excel_file_b):
    rows_a = read_excel_file(temp_excel_file_a)
    assert len(rows_a) == 1
    assert rows_a[0]["Customer Name"] == "Customer A"

    rows_b = read_excel_file(temp_excel_file_b)
    assert len(rows_b) == 2
    assert rows_b[0]["Customer Name"] == "Customer B1"
    assert rows_b[1]["Customer Name"] == "Customer B2"


def test_read_excel_file_missing_raises():
    with pytest.raises(FileNotFoundError, match="Input Excel file not found"):
        read_excel_file("non_existent_file_xyz.xlsx")


def test_read_excel_file_invalid_extension(tmp_path):
    txt_file = tmp_path / "data.txt"
    txt_file.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError, match="Input file must be an Excel file"):
        read_excel_file(txt_file)
