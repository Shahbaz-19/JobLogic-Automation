import pytest
from unittest.mock import AsyncMock, MagicMock
from app.automation.resolver import Resolver
from app.automation.processor import JobProcessor
from app.automation.audit_writer import AuditWriter, AUDIT_COLUMNS
from app.config import Settings


@pytest.fixture
def dummy_settings():
    return Settings(
        joblogic_tenant_id="00000000-0000-0000-0000-000000000001",
        joblogic_base_url="https://uatapi.joblogic.com/api/v1",
    )


@pytest.mark.anyio
async def test_find_tag_success(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(return_value={
        "Items": [
            {"Id": 1, "Name": "Success"},
            {"Id": 2, "Name": "Other Tag"}
        ]
    })

    resolver = Resolver(dummy_settings, mock_client)
    result = await resolver.find_tag("Success", "tenant-123")

    assert result is not None
    assert result["Name"] == "Success"


@pytest.mark.anyio
async def test_find_tag_not_found(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(return_value={"Items": []})

    resolver = Resolver(dummy_settings, mock_client)
    result = await resolver.find_tag("NonExistent", "tenant-123")

    assert result is None


@pytest.mark.anyio
async def test_find_tag_error_swallowed(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=Exception("API Error"))

    resolver = Resolver(dummy_settings, mock_client)
    result = await resolver.find_tag("Success", "tenant-123")

    assert result is None


@pytest.mark.anyio
async def test_process_row_success(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=[
        {"Items": [{"Id": 10, "UniqueId": "cust-guid", "Name": "Acme Corp"}]},  # Customer
        {"Items": [{"Id": 20, "UniqueId": "site-guid", "Name": "Main Site"}]},  # Site
        {"Items": [{"Id": 30, "Description": "Repair"}]},                       # Job Type
        {"Items": [{"UniqueId": "staff-uid-70", "FullName": "John Doe"}]},       # Staff GetAll
        {"IntId": 70, "UniqueId": "staff-uid-70", "Name": "John Doe"},           # Staff GetById
        {"Items": [{"Id": 40, "Description": "High"}]},                         # Job Priority
        {"Items": [{"Id": 50, "Description": "Plumbing"}]},                     # Job Category
        {"Items": [{"Id": 60, "Description": "Gas"}]},                          # Primary Job Trade
    ])

    processor = JobProcessor(dummy_settings, mock_client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Fix leaking pipe",
        "Job Type": "Repair",
        "Job Owner": "John Doe",
        "Job Priority": "High",
        "Job Category": "Plumbing",
        "Primary Job Trade": "Gas",
        "Order Number": "ORD-123",
        "Ref Number": "REF-456",
        "Notes": "Urgent attention",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="tenant-123",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
        verified_tags={"Success": True, "Partial Success": True},
    )

    assert result["status"] == "Success"
    assert result["job_action"] == "Ready"
    assert result["job_payload"]["Tags"] == ["Success"]
    assert result["tag_warning"] == ""
    assert result["job_payload"]["OrderNumber"] == "ORD-123"
    assert result["job_payload"]["ReferenceNumber"] == "REF-456"
    assert result["job_payload"]["AdditionalDetail"]["Trade"] == "Gas"
    assert result["job_payload"]["AdditionalDetail"]["OwnerUserId"] == 70


@pytest.mark.anyio
async def test_process_row_missing_job_owner(dummy_settings):
    mock_client = MagicMock()
    processor = JobProcessor(dummy_settings, mock_client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Fix leaking pipe",
        "Job Type": "Repair",
        "Job Owner": "",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="tenant-123",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
    )

    assert result["status"] == "Failed"
    assert result["job_action"] == "Not Created"
    assert "Job Owner" in result["missing_fields"]
    assert "Job Owner is required" in result["error"]
    assert mock_client.request.call_count == 0


@pytest.mark.anyio
async def test_process_row_unresolvable_job_owner(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=[
        {"Items": [{"Id": 10, "UniqueId": "cust-guid", "Name": "Acme Corp"}]},  # Customer
        {"Items": [{"Id": 20, "UniqueId": "site-guid", "Name": "Main Site"}]},  # Site
        {"Items": [{"Id": 30, "Description": "Repair"}]},                       # Job Type
        {"Items": [{"UniqueId": "uid-1", "Name": "Abdullah"}]},                 # Staff GetAll (Abdulla does not match)
    ])

    processor = JobProcessor(dummy_settings, mock_client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Fix leaking pipe",
        "Job Type": "Repair",
        "Job Owner": "Abdulla",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="tenant-123",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
    )

    assert result["status"] == "Failed"
    assert result["job_action"] == "Not Created"
    assert result["error"] == "Job Owner not found: Abdulla"


@pytest.mark.anyio
async def test_process_row_ambiguous_job_owner(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=[
        {"Items": [{"Id": 10, "UniqueId": "cust-guid", "Name": "Acme Corp"}]},  # Customer
        {"Items": [{"Id": 20, "UniqueId": "site-guid", "Name": "Main Site"}]},  # Site
        {"Items": [{"Id": 30, "Description": "Repair"}]},                       # Job Type
        {"Items": [
            {"UniqueId": "uid-1", "Name": "John Doe"},
            {"UniqueId": "uid-2", "Name": "John Doe"},
        ]},                                                                      # Staff GetAll (2 John Does)
    ])

    processor = JobProcessor(dummy_settings, mock_client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Fix leaking pipe",
        "Job Type": "Repair",
        "Job Owner": "John Doe",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="tenant-123",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
    )

    assert result["status"] == "Failed"
    assert result["job_action"] == "Not Created"
    assert "Job Owner is ambiguous: John Doe" in result["error"]


@pytest.mark.anyio
async def test_process_row_unresolvable_job_type(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=[
        {"Items": [{"Id": 10, "UniqueId": "cust-guid", "Name": "Acme Corp"}]},  # Customer
        {"Items": [{"Id": 20, "UniqueId": "site-guid", "Name": "Main Site"}]},  # Site
        {"Items": []},                                                           # Job Type (not found)
    ])

    processor = JobProcessor(dummy_settings, mock_client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Fix leaking pipe",
        "Job Type": "INVALID_JOB_TYPE_FOR_TEST",
        "Job Owner": "Abdul Basit",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="tenant-123",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
    )

    assert result["status"] == "Failed"
    assert result["job_action"] == "Not Created"
    assert result["error"] == "Job Type not found: INVALID_JOB_TYPE_FOR_TEST"


@pytest.mark.anyio
async def test_process_row_blank_optional_fields(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=[
        {"Items": [{"Id": 10, "UniqueId": "cust-guid", "Name": "Acme Corp"}]},  # Customer
        {"Items": [{"Id": 20, "UniqueId": "site-guid", "Name": "Main Site"}]},  # Site
        {"Items": [{"Id": 30, "Description": "Callout"}]},                      # Job Type
        {"Items": [{"UniqueId": "staff-uid-74", "FullName": "Abdul Basit"}]},    # Staff GetAll
        {"IntId": 74, "UniqueId": "staff-uid-74", "Name": "Abdul Basit"},        # Staff GetById
        {"Items": [{"Id": 50, "Description": "AC - Maintenance"}]},             # Job Category
        {"Items": [{"Id": 60, "Description": "Air Conditioning"}]},             # Primary Job Trade
    ])

    processor = JobProcessor(dummy_settings, mock_client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Routine equipment inspection",
        "Job Type": "Callout",
        "Job Owner": "Abdul Basit",
        "Job Priority": None,
        "Job Category": "AC - Maintenance",
        "Primary Job Trade": "Air Conditioning",
        "Order Number": None,
        "Ref Number": None,
        "Notes": "Notes present",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="tenant-123",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
        verified_tags={"Success": True, "Partial Success": True},
    )

    assert result["status"] == "Partial Success"
    assert result["job_action"] == "Ready"
    assert result["job_payload"]["Tags"] == ["Partial Success"]
    assert "Job Priority" in result["partial_fields"]
    assert "Order Number" in result["partial_fields"]
    assert "Ref Number" in result["partial_fields"]
    assert "OrderNumber" not in result["job_payload"]
    assert "ReferenceNumber" not in result["job_payload"]
    assert result["job_payload"]["AdditionalDetail"]["OwnerUserId"] == 74


@pytest.mark.anyio
async def test_process_row_invalid_optional_category(dummy_settings):
    mock_client = MagicMock()
    mock_client.request = AsyncMock(side_effect=[
        {"Items": [{"Id": 10, "UniqueId": "cust-guid", "Name": "Acme Corp"}]},  # Customer
        {"Items": [{"Id": 20, "UniqueId": "site-guid", "Name": "Main Site"}]},  # Site
        {"Items": [{"Id": 30, "Description": "Callout"}]},                      # Job Type
        {"Items": [{"UniqueId": "staff-uid-74", "FullName": "Abdul Basit"}]},    # Staff GetAll
        {"IntId": 74, "UniqueId": "staff-uid-74", "Name": "Abdul Basit"},        # Staff GetById
        {"Items": [{"Id": 40, "Description": "4-hour Response"}]},              # Job Priority
        {"Items": []},                                                           # Job Category (invalid)
        {"Items": [{"Id": 60, "Description": "Air Conditioning"}]},             # Primary Job Trade
    ])

    processor = JobProcessor(dummy_settings, mock_client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Optional category validation test",
        "Job Type": "Callout",
        "Job Owner": "Abdul Basit",
        "Job Priority": "4-hour Response",
        "Job Category": "INVALID_CATEGORY_FOR_TEST",
        "Primary Job Trade": "Air Conditioning",
        "Order Number": "NEW-007",
        "Ref Number": "REF-NEW-007",
        "Notes": "Notes present",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="tenant-123",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
        verified_tags={"Success": True, "Partial Success": True},
    )

    assert result["status"] == "Partial Success"
    assert result["job_action"] == "Ready"
    assert result["job_payload"]["Tags"] == ["Partial Success"]
    assert "Job Category" in result["partial_fields"]
    assert "JobCategory" not in result["job_payload"]
    assert result["job_payload"]["AdditionalDetail"]["OwnerUserId"] == 74


def test_audit_writer_tag_warning_column(tmp_path):
    audit_file = tmp_path / "test_audit.csv"
    writer = AuditWriter(str(audit_file))
    writer.reset()

    writer.write_row(
        row_number=2,
        source_row={"Customer Name": "Acme", "Site Name": "Site 1"},
        result={
            "status": "Partial Success",
            "tag_warning": "Tag 'Partial Success' not found in Joblogic (sent in payload)",
            "customer_external_id": "c1",
            "site_external_id": "s1",
            "job_external_id": "j1",
        }
    )

    content = audit_file.read_text(encoding="utf-8")
    assert "TagWarning" in content
    assert "Tag 'Partial Success' not found in Joblogic" in content


def test_audit_writer_timestamp_and_daily_path(tmp_path):
    """Verify Timestamp column is populated and default daily path format."""
    from app.automation.audit_writer import get_daily_audit_filename

    daily_path = get_daily_audit_filename()
    assert str(daily_path).startswith("audit\\audit_") or str(daily_path).startswith("audit/audit_")
    assert str(daily_path).endswith(".csv")

    test_file = tmp_path / "daily_test.csv"
    writer = AuditWriter(test_file)
    writer.write_row(
        row_number=2,
        source_row={"Customer Name": "Acme", "Site Name": "Site 1"},
        result={"status": "Success", "customer_external_id": "c1", "site_external_id": "s1", "job_external_id": "j1"}
    )

    content = test_file.read_text(encoding="utf-8")
    assert "Timestamp" in content
    lines = content.strip().splitlines()
    assert len(lines) == 2  # header + 1 row
    assert "T" in lines[1]  # ISO timestamp format e.g. 2026-08-25T18:36:00Z

