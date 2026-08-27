"""FastAPI dependencies shared by resource routers."""

from fastapi import Request

from app.clients.joblogic_client import JoblogicClient


def get_joblogic_client(request: Request) -> JoblogicClient:
    """Retrieve the lifecycle-managed client from application state."""

    return request.app.state.joblogic_client
