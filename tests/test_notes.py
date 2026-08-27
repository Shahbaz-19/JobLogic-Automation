import pytest
from unittest.mock import AsyncMock, MagicMock

from app.config import Settings
from app.joblogic.jobs.service import JobService
from app.automation.processor import JobProcessor


@pytest.mark.anyio
async def test_job_service_create_note_uses_note_endpoint():
    settings = Settings(
        joblogic_tenant_id="00000000-0000-0000-0000-000000000001",
        joblogic_base_url="https://uatapi.joblogic.com/api/v1",
    )
    client = MagicMock()
    client.request = AsyncMock(return_value={"Id": "note-id"})

    service = JobService(settings, client)
    payload = {
        "EntityId": "job-guid",
        "EntityType": 3,
        "NoteText": "API note verification test",
        "DateAdded": "2026-08-26T12:00:00.000Z",
        "IsPrivate": False,
        "Attachments": [],
        "Tags": [],
        "IsPrivateAndShowOnMobile": False,
        "TenantId": "00000000-0000-0000-0000-000000000001",
    }

    result = await service.create_note(payload)

    assert result == {"Id": "note-id"}
    client.request.assert_awaited_once_with(
        "POST",
        "/Note",
        json=payload,
    )


@pytest.mark.anyio
async def test_processor_does_not_send_notes_in_create_job_payload():
    settings = Settings(
        joblogic_tenant_id="00000000-0000-0000-0000-000000000001",
        joblogic_base_url="https://uatapi.joblogic.com/api/v1",
    )
    client = MagicMock()
    client.request = AsyncMock(side_effect=[
        {"Items": [{"Id": 10, "UniqueId": "cust-guid", "Name": "Acme Corp"}]},
        {"Items": [{"Id": 20, "UniqueId": "site-guid", "Name": "Main Site"}]},
        {"Items": [{"Id": 30, "Description": "Repair"}]},
        {"Items": [{"UniqueId": "staff-guid", "Name": "John Doe"}]},
        {"IntId": 70, "UniqueId": "staff-guid", "Name": "John Doe"},
    ])

    processor = JobProcessor(settings, client)
    row = {
        "Customer Name": "Acme Corp",
        "Site Name": "Main Site",
        "Job Description": "Fix leaking pipe",
        "Job Type": "Repair",
        "Job Owner": "John Doe",
        "Notes": "API note verification test",
    }

    result = await processor.process_row(
        row=row,
        tenant_id="00000000-0000-0000-0000-000000000001",
        customer_external_id="ext-c",
        site_external_id="ext-s",
        job_external_id="ext-j",
        verified_tags={"Success": True, "Partial Success": True},
    )

    assert result["status"] == "Partial Success"
    assert result["job_payload"].get("Notes") is None
