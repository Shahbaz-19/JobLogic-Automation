from pydantic import BaseModel, ConfigDict, Field


class SiteSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_by: int = Field(default=0, alias="OrderBy")
    search_term: str = Field(default="", alias="SearchTerm")
    tag_ids: str = Field(default="", alias="TagIds")
    include_inactive: bool = Field(default=True, alias="IncludeInactive")
    page_index: int = Field(default=1, alias="PageIndex")
    page_size: int = Field(default=10, alias="PageSize")
    tenant_id: str = Field(alias="TenantId")


class SiteListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="Id")
    unique_id: str = Field(alias="UniqueId")
    active: bool = Field(alias="Active")
    name: str = Field(alias="Name")
    address: str | None = Field(default=None, alias="Address")
    telephone: str | None = Field(default=None, alias="Telephone")
    email_address: str | None = Field(
        default=None,
        alias="EmailAddress",
    )
    reference_number: str | None = Field(
        default=None,
        alias="ReferenceNumber",
    )
    region: str | None = Field(default=None, alias="Region")
    postcode: str | None = Field(default=None, alias="Postcode")
    external_id: str | None = Field(
        default=None,
        alias="ExternalId",
    )
    address1: str | None = Field(default=None, alias="Address1")
    address2: str | None = Field(default=None, alias="Address2")
    address3: str | None = Field(default=None, alias="Address3")
    address4: str | None = Field(default=None, alias="Address4")
    account_number: str | None = Field(
        default=None,
        alias="AccountNumber",
    )


class SiteListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[SiteListItem] = Field(alias="Items")
    total_count: int = Field(alias="TotalCount")
    page_index: int = Field(alias="PageIndex")
    page_size: int = Field(alias="PageSize")


class SiteContact(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(alias="FirstName")
    last_name: str = Field(alias="LastName")
    telephone: str | None = Field(
        default=None,
        alias="Telephone",
    )
    email: str | None = Field(
        default=None,
        alias="Email",
    )
    position: str | None = Field(
        default=None,
        alias="Position",
    )


class SiteCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: str = Field(alias="CustomerId")
    external_id: str | None = Field(
        default=None,
        alias="ExternalId",
    )
    name: str = Field(alias="Name")
    address1: str | None = Field(
        default=None,
        alias="Address1",
    )
    address2: str | None = Field(
        default=None,
        alias="Address2",
    )
    address3: str | None = Field(
        default=None,
        alias="Address3",
    )
    address4: str | None = Field(
        default=None,
        alias="Address4",
    )
    postcode: str | None = Field(
        default=None,
        alias="Postcode",
    )
    telephone: str | None = Field(
        default=None,
        alias="Telephone",
    )
    region: str | None = Field(
        default=None,
        alias="Region",
    )
    reference_number: str | None = Field(
        default=None,
        alias="ReferenceNumber",
    )
    contacts: list[SiteContact] = Field(
        default_factory=list,
        alias="Contacts",
    )
    tags: list[str] = Field(
        default_factory=list,
        alias="Tags",
    )
    tenant_id: str = Field(alias="TenantId")


class SiteResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="Id")
    external_id: str | None = Field(
        default=None,
        alias="ExternalId",
    )
    name: str = Field(alias="Name")
    address1: str | None = Field(
        default=None,
        alias="Address1",
    )
    address2: str | None = Field(
        default=None,
        alias="Address2",
    )
    address3: str | None = Field(
        default=None,
        alias="Address3",
    )
    address4: str | None = Field(
        default=None,
        alias="Address4",
    )
    postcode: str | None = Field(
        default=None,
        alias="Postcode",
    )
    telephone: str | None = Field(
        default=None,
        alias="Telephone",
    )
    region: str | None = Field(
        default=None,
        alias="Region",
    )
    reference_number: str | None = Field(
        default=None,
        alias="ReferenceNumber",
    )
    contacts: list[dict] = Field(
        default_factory=list,
        alias="Contacts",
    )
    tags: list[str] = Field(
        default_factory=list,
        alias="Tags",
    )