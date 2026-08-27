"""FastAPI application composition and lifecycle management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.clients.joblogic_client import JoblogicClient
from app.config import get_settings
from app.core.exceptions import (
    JoblogicAPIError,
    JoblogicAuthenticationError,
    JoblogicTransportError,
)
from app.core.logging import configure_logging

from app.joblogic.base.router import router as base_router
from app.joblogic.customers.router import router as customers_router
from app.joblogic.sites.router import router as sites_router
from app.joblogic.jobs.router import router as jobs_router
from app.joblogic.staff.router import router as staff_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    settings = get_settings()

    # Configure application logging
    configure_logging(settings.log_level)

    # Store settings in application state
    app.state.settings = settings

    # Create and start shared Joblogic client
    app.state.joblogic_client = JoblogicClient(settings)

    await app.state.joblogic_client.start()

    yield

    # Close Joblogic HTTP clients on shutdown
    await app.state.joblogic_client.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )

    # ============================================================
    # ROUTES
    # ============================================================

    # Base / infrastructure routes
    app.include_router(base_router)

    # Customer routes
    app.include_router(customers_router)

    # Site routes
    app.include_router(sites_router)

    # Job routes
    app.include_router(jobs_router)

    # Staff routes
    app.include_router(staff_router)

    # ============================================================
    # EXCEPTION HANDLERS
    # ============================================================

    @app.exception_handler(JoblogicAPIError)
    async def joblogic_api_error_handler(
        _: Request,
        exc: JoblogicAPIError,
    ) -> JSONResponse:
        """
        Convert Joblogic API errors into a consistent response.

        Our API returns 502 because the failure occurred in the
        upstream Joblogic API.
        """

        return JSONResponse(
            status_code=502,
            content={
                "detail": exc.detail,
                "joblogic_status": exc.status_code,
                "joblogic_response": exc.response_body,
            },
        )

    @app.exception_handler(JoblogicTransportError)
    async def joblogic_transport_error_handler(
        _: Request,
        exc: JoblogicTransportError,
    ) -> JSONResponse:
        """Handle network/transport failures."""

        return JSONResponse(
            status_code=503,
            content={
                "detail": str(exc),
            },
        )

    @app.exception_handler(JoblogicAuthenticationError)
    async def joblogic_authentication_error_handler(
        _: Request,
        exc: JoblogicAuthenticationError,
    ) -> JSONResponse:
        """Handle Joblogic authentication failures."""

        return JSONResponse(
            status_code=503,
            content={
                "detail": str(exc),
            },
        )

    return app


app = create_app()