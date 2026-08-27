# Missing endpoints and implementation blockers

| Required functionality | Documentation result | Safe action |
| --- | --- | --- |
| Dedicated tag creation | No create-tag operation is in the collection. It provides search, get, and update; update requires existing `UniqueId`. | Do not make a separate create call. UAT-test whether Job creation with a string tag creates it; otherwise pre-provision tags with Joblogic. |
| Guaranteed unknown-tag behavior | `POST /Job` accepts string tags but does not state whether unknown tags are created or rejected. | Treat as unverified until UAT tested; audit the outcome. |
| External-ID lookup confirmation | Customer search explicitly supports external-ID searching. The Site search request example includes `SearchCondition`, and Joblogic returns ExternalId in results, but published documentation does not explicitly define ExternalId filtering for Site/Job searches. | Generate the documented `JLA-{C|S|J}-{hash}` values and UAT-test exact lookup for Site and Job before enabling writes. Use a local idempotency record if either API cannot search it. |
| Staff ID extraction | Job creation requires integer `AdditionalDetail.OwnerUserId`, but the Staff search response schema is absent from the collection. | Inspect an authenticated UAT response and record the exact ID field. |

## Mandatory business safeguards

The API may auto-create unknown Job Type, Job Category, and Priority strings. This automation must not rely on that behavior:

- Unmatched mandatory Job Type: fail the row before job creation.
- Unmatched optional Category, Priority, or Trade: omit it, audit it, and return partial success if job creation succeeds.
