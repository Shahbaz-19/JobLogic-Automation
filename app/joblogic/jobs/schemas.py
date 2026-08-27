
from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# COMMON CONTACT
# ============================================================

class JobContact(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(alias="FirstName")
    last_name: str = Field(alias="LastName")
    telephone: str | None = Field(default=None, alias="Telephone")
    email: str | None = Field(default=None, alias="Email")
    position: str | None = Field(default=None, alias="Position")


# ============================================================
# JOB NOTE
# ============================================================

class JobNote(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    note_text: str = Field(alias="NoteText")
    author: str | None = Field(default=None, alias="Author")
    date_added: str | None = Field(default=None, alias="DateAdded")
    is_private: bool = Field(default=False, alias="IsPrivate")


# ============================================================
# ADDITIONAL JOB DETAILS
# ============================================================

class JobAdditionalDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    trade: str | None = Field(default=None, alias="Trade")

    # Temporarily optional because Staff API is unavailable
    owner_user_id: int | None = Field(
        default=None,
        alias="OwnerUserId",
    )

    next_contact_date: str | None = Field(
        default=None,
        alias="NextContactDate",
    )

    is_require_approval: bool | None = Field(
        default=None,
        alias="IsRequireApproval",
    )

    quoted_value: float | None = Field(
        default=None,
        alias="QuotedValue",
    )

    job_ref1: str | None = Field(
        default=None,
        alias="JobRef1",
    )

    job_ref2: str | None = Field(
        default=None,
        alias="JobRef2",
    )

    secondary_trade_ids: list[str] = Field(
        default_factory=list,
        alias="SecondaryTradeIds",
    )


# ============================================================
# CREATE JOB
# ============================================================

class JobCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    external_id: str | None = Field(
        default=None,
        alias="ExternalId",
    )

    customer: dict = Field(alias="Customer")
    site: dict = Field(alias="Site")

    description: str = Field(alias="Description")

    status: str = Field(
        default="New Job",
        alias="Status",
    )

    job_type: str = Field(alias="JobType")

    job_category: str | None = Field(
        default=None,
        alias="JobCategory",
    )

    priority_level: str | None = Field(
        default=None,
        alias="PriorityLevel",
    )

    order_number: str | None = Field(
        default=None,
        alias="OrderNumber",
    )

    reference_number: str | None = Field(
        default=None,
        alias="ReferenceNumber",
    )

    date_logged: str | None = Field(
        default=None,
        alias="DateLogged",
    )

    preferred_appointment_date: str | None = Field(
        default=None,
        alias="PreferredAppointmentDate",
    )

    target_completion_date: str | None = Field(
        default=None,
        alias="TargetCompletionDate",
    )

    date_complete: str | None = Field(
        default=None,
        alias="DateComplete",
    )

    tags: list[str] = Field(
        default_factory=list,
        alias="Tags",
    )

    contacts: list[JobContact] = Field(
        default_factory=list,
        alias="Contacts",
    )

    notes: list[JobNote] = Field(
        default_factory=list,
        alias="Notes",
    )

    additional_detail: JobAdditionalDetail | None = Field(
        default=None,
        alias="AdditionalDetail",
    )

    tenant_id: str = Field(alias="TenantId")


# ============================================================
# SEARCH JOBS
# ============================================================

class JobSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: int | None = Field(
        default=None,
        alias="CustomerId",
    )

    site_id: int | None = Field(
        default=None,
        alias="SiteId",
    )

    start_date: str = Field(
        default="",
        alias="StartDate",
    )

    end_date: str = Field(
        default="",
        alias="EndDate",
    )

    start_logged_date: str = Field(
        default="",
        alias="StartLoggedDate",
    )

    end_logged_date: str = Field(
        default="",
        alias="EndLoggedDate",
    )

    start_complete_date: str = Field(
        default="",
        alias="StartCompleteDate",
    )

    end_complete_date: str = Field(
        default="",
        alias="EndCompleteDate",
    )

    status_ids: str = Field(
        default="",
        alias="StatusIds",
    )

    category_ids: str = Field(
        default="",
        alias="CategoryIds",
    )

    type_ids: str = Field(
        default="",
        alias="TypeIds",
    )

    priority_ids: str = Field(
        default="",
        alias="PriorityIds",
    )

    owner_ids: str = Field(
        default="",
        alias="OwnerIds",
    )

    area_ids: str = Field(
        default="",
        alias="AreaIds",
    )

    trade_ids: str = Field(
        default="",
        alias="TradeIds",
    )

    exclude_tag_ids: str = Field(
        default="",
        alias="ExcludeTagIds",
    )

    only_include_primary_job_trade: bool = Field(
        default=True,
        alias="OnlyIncludePrimaryJobTrade",
    )

    include_reactive_jobs: bool = Field(
        default=True,
        alias="IncludeReactiveJobs",
    )

    include_ppm_jobs: bool = Field(
        default=True,
        alias="IncludePPMJobs",
    )

    include_portal_link: bool = Field(
        default=True,
        alias="IncludePortalLink",
    )

    include_tags: bool = Field(
        default=True,
        alias="IncludeTags",
    )

    include_contacts: bool = Field(
        default=True,
        alias="IncludeContacts",
    )

    include_notes: bool = Field(
        default=True,
        alias="IncludeNotes",
    )

    order_by: int = Field(
        default=0,
        alias="OrderBy",
    )

    search_term: str = Field(
        default="",
        alias="SearchTerm",
    )

    tag_ids: str = Field(
        default="",
        alias="TagIds",
    )

    include_inactive: bool = Field(
        default=True,
        alias="IncludeInactive",
    )

    page_index: int = Field(
        default=1,
        alias="PageIndex",
    )

    page_size: int = Field(
        default=10,
        alias="PageSize",
    )

    tenant_id: str = Field(alias="TenantId")


# ============================================================
# LOOKUP REQUESTS
# ============================================================

class JobTypeSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    search_term: str | None = Field(
        default=None,
        alias="SearchTerm",
    )

    tenant_id: str = Field(alias="TenantId")


class JobCategorySearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    search_term: str | None = Field(
        default=None,
        alias="SearchTerm",
    )

    page_index: int = Field(
        default=1,
        alias="PageIndex",
    )

    page_size: int = Field(
        default=10,
        alias="PageSize",
    )

    tenant_id: str = Field(alias="TenantId")


class PrioritySearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    search_term: str | None = Field(
        default=None,
        alias="SearchTerm",
    )

    include_inactive: bool = Field(
        default=True,
        alias="IncludeInactive",
    )

    page_index: int = Field(
        default=1,
        alias="PageIndex",
    )

    page_size: int = Field(
        default=10,
        alias="PageSize",
    )

    tenant_id: str = Field(alias="TenantId")


class TradeSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tenant_id: str = Field(alias="tenantId")

    search_term: str = Field(
        default="",
        alias="searchTerm",
    )

    page_index: int = Field(
        default=1,
        alias="pageIndex",
    )

    page_size: int = Field(
        default=10,
        alias="pageSize",
    )


# ============================================================
# GENERIC API RESPONSE
# ============================================================

class JobResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
    )

    id: str | None = Field(
        default=None,
        alias="Id",
    )

    external_id: str | None = Field(
        default=None,
        alias="ExternalId",
    )

    description: str | None = Field(
        default=None,
        alias="Description",
    )

    status: str | None = Field(
        default=None,
        alias="Status",
    )
