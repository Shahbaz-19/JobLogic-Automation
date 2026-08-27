"""Single-run entry point for the JobLogic automation.

Usage
-----
Run one scheduled execution (input from CLI):
    python run_automation.py --input "TestAutomation/joblogic_full_condition_test_data.xlsx"

Run one scheduled execution (input from .env EXCEL_INPUT_FILE):
    python run_automation.py

Display the production schedule (no API calls, no job creation):
    python run_automation.py --check-schedule
"""

import argparse
import asyncio
import sys

from app.config import get_settings
from app.clients.joblogic_client import JoblogicClient
from app.automation.runner import AutomationRunner


# ---------------------------------------------------------------------------
# Production schedule constants
# ---------------------------------------------------------------------------

SCHEDULE_TIMEZONE = "Europe/London"
SCHEDULE_CRON = "0 8-16 * * 1-5"
SCHEDULE_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
SCHEDULE_HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16]


def show_schedule() -> None:
    """Print the production schedule and exit.  Makes no API calls."""
    print("Automation Schedule")
    print("-------------------")
    print(f"Timezone: {SCHEDULE_TIMEZONE}")
    print(f"Cron:     {SCHEDULE_CRON}")
    print()
    print("Runs:")
    for day in SCHEDULE_DAYS:
        for hour in SCHEDULE_HOURS:
            print(f"  {day} {hour:02d}:00")
    print()
    print("No run at 17:00.")
    print("No run on Saturday or Sunday.")
    print()
    print(
        f"Total executions per week: "
        f"{len(SCHEDULE_DAYS) * len(SCHEDULE_HOURS)}"
    )


async def main(input_file: str | None = None, audit_file: str | None = None) -> None:
    settings = get_settings()

    # Resolve and log the input file path before starting the HTTP client,
    # so a misconfigured path surfaces immediately at startup.
    dummy_runner = AutomationRunner(
        settings=settings,
        client=None,  # type: ignore[arg-type]
        audit_file=audit_file,
    )
    try:
        resolved_path = dummy_runner.resolve_input_file(input_file)
        print(f"Input Excel file: {resolved_path}")
    except (ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    client = JoblogicClient(settings)
    await client.start()

    try:
        runner = AutomationRunner(
            settings=settings,
            client=client,
            audit_file=audit_file,
        )

        await runner.run(excel_file=input_file)

    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "JobLogic Automation Runner — executes ONE automation run "
            "and exits. The production scheduler invokes this once per "
            "scheduled cron trigger."
        )
    )
    parser.add_argument(
        "--input",
        "-i",
        dest="input_file",
        type=str,
        default=None,
        help=(
            "Path to Excel input file (.xlsx or .xls). "
            "Overrides EXCEL_INPUT_FILE."
        ),
    )
    parser.add_argument(
        "--audit",
        "-a",
        dest="audit_file",
        type=str,
        default=None,
        help=(
            "Optional custom audit file path. "
            "Defaults to daily file: audit/audit_YYYY-MM-DD.csv."
        ),
    )
    parser.add_argument(
        "--check-schedule",
        action="store_true",
        dest="check_schedule",
        help=(
            "Display the production cron schedule and exit. "
            "Makes no API calls and creates no jobs."
        ),
    )
    args = parser.parse_args()

    if args.check_schedule:
        show_schedule()
        sys.exit(0)

    asyncio.run(main(input_file=args.input_file, audit_file=args.audit_file))