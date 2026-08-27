# Workflow Decision Record

## Per-Row Processing Flow
For each Excel row:
1. Validate mandatory values (`Customer Name`, `Site Name`, `Job Description`, `Job Type`, `Job Owner`).
2. Resolve or create Customer (`POST /Customer/GetAll` -> `POST /Customer/Create`).
3. Resolve or create customer-scoped Site (`POST /Site/GetAll` -> `POST /Site/Create`).
4. Exact-match Job Type (`POST /JobType/GetAll`).
5. Resolve active Staff owner and numeric integer Staff ID (`POST /staff/GetAll` -> `GET /staff?uniqueId=...`).
6. Resolve optional values (`Priority`, `Category`, `Trade`, `Order Number`, `Ref Number`, `Notes`).
7. Construct payload with outcome tag (`Success` or `Partial Success`).
8. Create Job via JobLogic API.
9. Append results to `output/job_results.csv` and record full audit entry in `audit.csv`.
10. Continue to the next row regardless of outcome (row-level isolation).

## Automation Schedule
The production scheduler triggers the single-run automation (`run_automation.py`) once per scheduled execution:
- **Timezone**: `Europe/London`
- **Cron Expression**: `0 8-16 * * 1-5`
- **Window**: Monday through Friday, 08:00 to 16:00 UK local time
- **Executions**: 08:00, 09:00, 10:00, 11:00, 12:00, 13:00, 14:00, 15:00, 16:00 (9 runs/day, 45/week)
- **No execution**: 17:00, Saturday, Sunday.

Inspect the schedule locally using:
```bash
python run_automation.py --check-schedule
```

