# JobLogicAutomation

FastAPI backend foundation and automation engine for Joblogic integration.

## Run locally

1. Create and activate a virtual environment.
2. Install `requirements.txt`.
3. Copy `.env.example` to `.env` and configure your credentials and `EXCEL_INPUT_FILE`.
4. Start web server with `python run.py` (or `python run.py --server`) and use `GET /health`.

## Run Automation

Run the Excel-to-JobLogic automation via the single-run entry point:

```bash
# Provide explicit input file (overrides EXCEL_INPUT_FILE)
python run_automation.py --input "TestAutomation/your_file.xlsx"

# Use configured EXCEL_INPUT_FILE from .env
python run_automation.py
```

### Input Priority

1. CLI argument: `--input <path>` (or `-i <path>`)
2. Environment configuration: `EXCEL_INPUT_FILE` in `.env`
3. If neither is specified or if the file does not exist, automation exits with a clear descriptive error.

The absolute path of the resolved input file is printed at startup:

```
Input Excel file: C:\...\TestAutomation\your_file.xlsx
```

### Single-run behaviour

One invocation of `run_automation.py`:

1. Reads the specified Excel file.
2. Processes all rows.
3. Creates / validates Customer and Site.
4. Resolves Job Owner.
5. Validates Job Type.
6. Resolves optional fields (Priority, Category, Trade, Order Number, Ref, Notes).
7. Creates jobs where appropriate.
8. Captures actual Job Number and Job ID from the API response.
9. Appends results to `output/job_results.csv`.
10. Writes / updates `audit.csv`.
11. Exits.

The process terminates automatically. There is no loop, no sleep, and no background thread.

Audit results are written to `audit.csv`.

---

## Automation Schedule

The production scheduler triggers `run_automation.py` once per scheduled cron execution.

```
Timezone:
Europe/London

Cron:
0 8-16 * * 1-5

Execution window:
Monday–Friday
08:00–16:00 UK local time

Runs:
08:00
09:00
10:00
11:00
12:00
13:00
14:00
15:00
16:00

No execution:
17:00
Saturday
Sunday
```

Total: **9 executions per working day, 45 per week.**

> **Timezone note:** The cron expression itself carries no timezone information.
> The `Europe/London` timezone must be configured at the **scheduler level**
> (e.g. the system crontab, Task Scheduler, CI runner, or managed cron service).

### Verify the schedule locally

To inspect the configured schedule without making any API calls or creating any jobs:

```bash
python run_automation.py --check-schedule
```

Example output:

```
Automation Schedule
-------------------
Timezone: Europe/London
Cron:     0 8-16 * * 1-5

Runs:
  Monday 08:00
  Monday 09:00
  ...
  Friday 16:00

No run at 17:00.
No run on Saturday or Sunday.

Total executions per week: 45
```

---

## Output Files

| File | Description |
|---|---|
| `output/job_results.csv` | Master business results file (Job Number, Job ID, Status). **Appended** on every hourly run — never truncated. |
| `audit/audit_YYYY-MM-DD.csv` | Daily date-stamped audit log with UTC timestamp for each row. Automatically created daily; all 9 hourly runs for the day accumulate cleanly. |

Job Number and Job ID are written **only** when returned by the actual JobLogic API. No fake or placeholder values are generated.

---

## Idempotency

Each Excel row is assigned a deterministic SHA-256 `ExternalId` (derived from its content fields) and sent in the job creation payload as `ExternalId`.

> **Risk:** Whether the JobLogic API uses `ExternalId` to prevent duplicate job creation (i.e. returns the existing job rather than creating a new one) has **not been confirmed in UAT**.
>
> If the same Excel file is submitted on every hourly run without modification, and the API does not honour `ExternalId` for deduplication, the same row will produce a new job on each execution.
>
> This **must be verified in UAT** before deploying the hourly schedule against a live Excel file that does not change between runs.

## Job Notes

The Excel `Notes` column is created as a JobLogic Job Note after the Job is successfully created.

The automation uses:

- `POST /api/v1/Note`
- `EntityId` = the created Job ID returned by the Create Job API
- `EntityType` = `3`
- `NoteText` = the Excel `Notes` value
- `TenantId` = configured JobLogic tenant
- `Attachments` = `[]`
- `Tags` = `[]`

Blank Notes do not trigger a Note API request. If the Job is created but the Note API fails, the row is recorded as `Partial Success` with the actual Job Number/Job ID preserved.

