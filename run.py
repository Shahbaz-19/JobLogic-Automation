"""Local application entry point."""

import argparse
import asyncio
import uvicorn

from app.automation.runner import AutomationRunner
from app.clients.joblogic_client import JoblogicClient
from app.config import get_settings


async def run_automation_cli(input_file: str | None) -> None:
    settings = get_settings()
    client = JoblogicClient(settings)
    await client.start()
    try:
        runner = AutomationRunner(
            settings=settings,
            client=client,
            audit_file=None,
        )
        await runner.run(excel_file=input_file)
    finally:
        await client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobLogic Automation & Server Entry Point")
    parser.add_argument(
        "--input",
        "-i",
        dest="input_file",
        type=str,
        default=None,
        help="Path to Excel input file (.xlsx or .xls) to run the automation.",
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Run the FastAPI application server.",
    )
    args, unknown = parser.parse_known_args()

    if args.input_file is not None:
        asyncio.run(run_automation_cli(input_file=args.input_file))
    else:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
