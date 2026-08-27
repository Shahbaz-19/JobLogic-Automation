# Audit Format & Specification

The automation records an append-safe, structured audit log to a daily date-stamped file under `audit/` (e.g., `audit/audit_YYYY-MM-DD.csv`) for every processed Excel row.

## CSV Columns

| Column | Description |
|---|---|
| `Timestamp` | ISO-8601 UTC timestamp of execution (e.g., `2026-08-25T08:00:15Z`) |
| `RowNumber` | 1-based Excel row number (header is row 1, first data row is 2) |
| `CustomerName` | Customer name from the Excel row |
| `SiteName` | Site name from the Excel row |
| `CustomerExternalId` | Deterministic SHA-256 ID (`JLA-C-...`) |
| `SiteExternalId` | Deterministic SHA-256 ID (`JLA-S-...`) |
| `JobExternalId` | Deterministic SHA-256 ID (`JLA-J-...`) |
| `Status` | `Success`, `Partial Success`, or `Failed` |
| `CustomerAction` | `Found`, `Created`, or `Error` |
| `SiteAction` | `Found`, `Created`, or `Error` |
| `JobAction` | `Created` or `Not Created` |
| `MissingFields` | Comma-separated list of missing mandatory fields |
| `PartialFields` | Comma-separated list of omitted/unresolved optional fields |
| `TagWarning` | Warning message if outcome tag was not confirmed in pre-run check |
| `Error` | Detailed error diagnostic message (if status is `Failed`) |

## Daily Rotation & Persistence
- **Daily Rotation**: A new audit file is automatically created for each day (`audit/audit_YYYY-MM-DD.csv`).
- **Append-Safe**: All 9 hourly runs across the same working day accumulate into that day's file via `initialize()`.
- **Security**: Passwords, client secrets, and bearer tokens are **never** logged or written to audit files.


