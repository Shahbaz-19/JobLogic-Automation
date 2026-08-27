from pydantic import BaseModel, ConfigDict, Field


class BillingDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    enable_billing_address: bool | None = Field(
        default=None,
        alias="EnableBillingAddress",
    )
    name: str | None = Field(default=None, alias="Name")
    address1: str | None = Field(default=None, alias="Address1")
    address2: str | None = Field(default=None, alias="Address2")
    address3: str | None = Field(default=None, alias="Address3")
    address4: str | None = Field(default=None, alias="Address4")
    postcode: str | None = Field(default=None, alias="Postcode")
    telephone: str | None = Field(default=None, alias="Telephone")
    email_address: str | None = Field(default=None, alias="EmailAddress")
    account_number: str | None = Field(default=None, alias="AccountNumber")
    other_emails: str | None = Field(default=None, alias="OtherEmails")


class InvoiceDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    payment_due: int | None = Field(default=None, alias="PaymentDue")
    payment_term: str | None = Field(default=None, alias="PaymentTerm")


class AdditionalDetails(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    account_number: str | None = Field(default=None, alias="AccountNumber")
    vat_number: str | None = Field(default=None, alias="VATNumber")
    account_manager: int | None = Field(default=None, alias="AccountManager")
    billing_details: BillingDetails | None = Field(
        default=None,
        alias="BillingDetails",
    )
    invoice_details: InvoiceDetails | None = Field(
        default=None,
        alias="InvoiceDetails",
    )


class CustomerContact(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    first_name: str = Field(alias="FirstName")
    last_name: str = Field(alias="LastName")
    telephone: str | None = Field(default=None, alias="Telephone")
    country_code: str | None = Field(default=None, alias="CountryCode")
    email: str | None = Field(default=None, alias="Email")
    position: str | None = Field(default=None, alias="Position")
    is_primary: bool = Field(default=False, alias="IsPrimary")


class CustomerCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    is_prospect: bool | None = Field(default=None, alias="IsProspect")
    external_id: str | None = Field(default=None, alias="ExternalId")
    name: str = Field(alias="Name")
    address1: str | None = Field(default=None, alias="Address1")
    address2: str | None = Field(default=None, alias="Address2")
    address3: str | None = Field(default=None, alias="Address3")
    address4: str | None = Field(default=None, alias="Address4")
    postcode: str | None = Field(default=None, alias="Postcode")
    telephone: str | None = Field(default=None, alias="Telephone")
    customer_type: str | None = Field(default=None, alias="CustomerType")
    reference_number: str | None = Field(
        default=None,
        alias="ReferenceNumber",
    )

    contacts: list[CustomerContact] = Field(
        default_factory=list,
        alias="Contacts",
    )

    tags: list[str] = Field(
        default_factory=list,
        alias="Tags",
    )

    additional_details: AdditionalDetails | None = Field(
        default=None,
        alias="AdditionalDetails",
    )

    tenant_id: str = Field(alias="TenantId")


class CustomerResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="Id")
    external_id: str | None = Field(default=None, alias="ExternalId")
    name: str = Field(alias="Name")
    address1: str | None = Field(default=None, alias="Address1")
    address2: str | None = Field(default=None, alias="Address2")
    address3: str | None = Field(default=None, alias="Address3")
    address4: str | None = Field(default=None, alias="Address4")
    postcode: str | None = Field(default=None, alias="Postcode")
    telephone: str | None = Field(default=None, alias="Telephone")
    customer_type: str | None = Field(default=None, alias="CustomerType")
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
    is_prospect: bool | None = Field(
        default=None,
        alias="IsProspect",
    )

class CustomerSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    search_term: str = Field(default="", alias="SearchTerm")
    search_condition: int = Field(default=0, alias="SearchCondition")
    tag_ids: str = Field(default="", alias="TagIds")
    include_inactive: bool = Field(default=True, alias="IncludeInactive")
    order_by: int = Field(default=0, alias="OrderBy")
    page_index: int = Field(default=1, alias="PageIndex")
    page_size: int = Field(default=10, alias="PageSize")
    tenant_id: str = Field(alias="TenantId")


class CustomerListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int = Field(alias="Id")
    unique_id: str = Field(alias="UniqueId")
    name: str = Field(alias="Name")
    active: bool = Field(alias="Active")
    address: str | None = Field(default=None, alias="Address")
    postcode: str | None = Field(default=None, alias="Postcode")
    contact: str | None = Field(default=None, alias="Contact")
    email_address: str | None = Field(default=None, alias="EmailAddress")
    telephone: str | None = Field(default=None, alias="Telephone")
    account_number: str | None = Field(default=None, alias="AccountNumber")
    custom_reference: str | None = Field(default=None, alias="CustomReference")
    customer_telephone: str | None = Field(
        default=None,
        alias="CustomerTelephone",
    )
    external_id: str | None = Field(default=None, alias="ExternalId")


class CustomerListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[CustomerListItem] = Field(alias="Items")
    total_count: int = Field(alias="TotalCount")
    page_index: int = Field(alias="PageIndex")
    page_size: int = Field(alias="PageSize")

class CustomerDetailsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="Id")
    external_id: str | None = Field(default=None, alias="ExternalId")
    name: str = Field(alias="Name")
    address: str | None = Field(default=None, alias="Address")
    address1: str | None = Field(default=None, alias="Address1")
    address2: str | None = Field(default=None, alias="Address2")
    address3: str | None = Field(default=None, alias="Address3")
    address4: str | None = Field(default=None, alias="Address4")
    postcode: str | None = Field(default=None, alias="Postcode")
    telephone: str | None = Field(default=None, alias="Telephone")
    customer_type: str | None = Field(default=None, alias="CustomerType")
    account_number: str | None = Field(default=None, alias="AccountNumber")
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
    additional_details: dict | None = Field(
        default=None,
        alias="AdditionalDetails",
    )
    int_id: int = Field(alias="IntId")

