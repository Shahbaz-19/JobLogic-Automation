# Joblogic API mapping

**Source reviewed:** Joblogic's published [API documentation](https://apidocs.joblogic.com/) and linked public Postman collection, 2026-08-20. The UAT base URL is `https://uatapi.joblogic.com/api/v1`; production access, tenant ID, credentials, and source-IP allowlisting must be obtained from Joblogic.

All resource calls require a bearer token and `TenantId`. Obtain a token with `POST https://uatidentityserver.joblogic.com/connect/token`, form fields `client_id`, `client_secret`, `grant_type=client_credentials`, and `scope=JL.Api`.

| Requirement | Endpoint | Method | Available? | Implemented? | Notes |
| --- | --- | --- | --- | --- | --- |
| Search customer | `/Customer/GetAll` | POST | Yes | No | Search `Items[].Name` exactly. |
| Create customer | `/Customer` | POST | Yes | No | Requires `ExternalId`, `Name`, `TenantId`. |
| Search site | `/Site/GetAll` | POST | Yes | No | Scope with Customer's integer `CustomerId`; exact-match name. |
| Create site | `/Site` | POST | Yes | No | Requires customer GUID, `ExternalId`, `Name`, `TenantId`. |
| Search staff | `/staff/GetAll` | POST | Yes | No | Resolve active exact match; request supports search and pagination. |
| Search job type | `/jobtype/GetAll` | POST | Yes | No | Response includes `Description`, `Id`, and `UniqueId`; Job create accepts the description string. |
| Search category | `/JobCategory/GetAll` | POST | Yes | No | Job create accepts a description string. |
| Search priority | `/Priority/GetAll` | POST | Yes | No | Job create accepts a description string. |
| Search trade | `/Trade/GetAll` | POST | Yes | No | Job field requires an existing trade description. |
| Search tag | `/Tag/GetAll` | POST | Yes | No | Search before use; creation behavior needs UAT verification. |
| Get/update tag | `/Tag/GetById`, `/Tag/UpdateTag` | GET, POST | Yes | No | Update requires existing `UniqueId`; no tag-create operation is exposed. |
| Create job | `/Job` | POST | Yes | No | Customer/Site IDs are GUIDs; set documented `Status: "New Job"`. |
| Search/get job | `/Job/getall`, `/Job/GetById`, `/Job` | POST, GET | Yes | No | Use after agreeing an external-ID/idempotency strategy. |

| Excel field | Mandatory | Resolution | Job-create field | Invalid/missing behavior |
| --- | --- | --- | --- | --- |
| Customer Name | Yes | Customer search/create | `Customer.Id` (GUID) | Fail row if unresolved. |
| Site Name | Yes | Customer-scoped site search/create | `Site.Id` (GUID) | Fail row if unresolved. |
| Job Description | Yes | Plain text | `Description` | Fail if blank. |
| Job Type | Yes | Exact-match `/jobtype/GetAll` by description | `JobType` string | Fail if unmatched. |
| Job Owner | Yes | Exact-match active `/staff/GetAll` result | `AdditionalDetail.OwnerUserId` integer | Fail if unmatched; confirm Staff response ID field in UAT. |
| Job Priority | No | Exact-match `/Priority/GetAll` | `PriorityLevel` string | Omit and mark partial success if unmatched. |
| Job Category | No | Exact-match `/JobCategory/GetAll` | `JobCategory` string | Omit and mark partial success if unmatched. |
| Primary Job Trade | No | Exact-match `/Trade/GetAll` | `AdditionalDetail.Trade` string | Omit and mark partial success if unmatched. |
| Order Number | No | Plain text | `OrderNumber` | Omit if blank. |
| Ref Number | No | Plain text | `ReferenceNumber` | Omit if blank. |
| Notes | No | Plain text | `Notes[]` | Omit if blank. |

## Generated external IDs and rerun safety

The documented `POST /Customer`, `POST /Site`, and `POST /Job` request schemas each accept a string `ExternalId`; each create response also returns that value. The automation will generate it at runtime rather than add an Excel column.

Use this versioned, deterministic format (well below the documented 255-character limits where one is stated):

| Entity | Canonical identity input | Generated value |
| --- | --- | --- |
| Customer | `v1|customer|{normalised Customer Name}` | `JLA-C-{first 32 lowercase hex characters of SHA-256}` |
| Site | `v1|site|{customer ExternalId}|{normalised Site Name}` | `JLA-S-{first 32 lowercase hex characters of SHA-256}` |
| Job | `v1|job|{customer ExternalId}|{site ExternalId}|{canonical JSON of all eleven Excel field values}` | `JLA-J-{first 32 lowercase hex characters of SHA-256}` |

Normalisation is Unicode NFC, trim leading/trailing whitespace, collapse internal whitespace, and casefold. Canonical JSON uses the exact documented Excel header order and `null` for empty optional values. The input must never contain credentials. The `v1` prefix makes a future format migration explicit.

Before every create, search for the same generated ExternalId and exact-match the response ExternalId; use that record when found. Customer search explicitly documents `SearchCondition: 1` for ExternalId. Site search includes `SearchCondition` in the published request example and returns `Items[].ExternalId`; Job search returns job data but its ExternalId-specific filter is not explicitly documented. Both Site and Job external-ID lookup behavior must be confirmed with a non-production UAT request before enabling writes. If not supported, persist the generated value and returned Joblogic identifiers in the local audit/idempotency store before retrying a create.

This guarantees idempotency for a re-run of the same logical row. It cannot distinguish two intentionally separate jobs with identical eleven-field input; add a stable source-record key to the input when that business case exists.

## Tags and safeguards

`POST /Job` accepts `Tags: IEnumerable<string>` — tag names, not IDs. It does not document whether unknown names are automatically created. Search `Success` and `Partial Success`, then only pass the documented string form after UAT confirms the behavior. Do not invent a tag-create call.

The Job-create endpoint documents auto-creation of unknown Job Type, Category, and Priority strings. This conflicts with the business requirement. The workflow must search and exact-match first: unknown Job Type fails the row; unknown optional values are omitted and produce `Partial Success` after a successful job create.

Joblogic documents a default 100-request/minute limit and UTC datetime values. The later schedule is `0 8-17 * * 1-5` in `Europe/London`.
