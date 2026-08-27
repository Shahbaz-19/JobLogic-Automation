from pydantic import BaseModel, ConfigDict, Field


class StaffListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    unique_id: str = Field(alias="UniqueId")
    name: str = Field(alias="Name")
    active: bool = Field(default=True, alias="Active")
    staff_type: int | None = Field(default=None, alias="StaffType")
    email_address: str | None = Field(default=None, alias="EmailAddress")
    telephone: str | None = Field(default=None, alias="Telephone")
    mobile: str | None = Field(default=None, alias="Mobile")


class StaffListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[StaffListItem] = Field(default_factory=list, alias="Items")
    total_count: int = Field(default=0, alias="TotalCount")
    page_index: int = Field(default=1, alias="PageIndex")
    page_size: int = Field(default=50, alias="PageSize")


class StaffSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    search_term: str = Field(default="", alias="SearchTerm")
    include_inactive: bool = Field(default=False, alias="IncludeInactive")
    page_index: int = Field(default=1, alias="PageIndex")
    page_size: int = Field(default=50, alias="PageSize")
    tenant_id: str = Field(alias="TenantId")


class StaffDetailsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    int_id: int = Field(alias="IntId")
    unique_id: str = Field(alias="UniqueId")
    name: str = Field(alias="Name")
    active: bool = Field(default=True, alias="Active")
    staff_type: int | None = Field(default=None, alias="StaffType")
    email_address: str | None = Field(default=None, alias="EmailAddress")
    telephone: str | None = Field(default=None, alias="Telephone")
    mobile: str | None = Field(default=None, alias="Mobile")
    reference: str | None = Field(default=None, alias="Reference")
    other: str | None = Field(default=None, alias="Other")
