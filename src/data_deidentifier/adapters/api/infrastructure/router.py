from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.data_deidentifier.adapters.api.dependencies import get_health_check_service
from src.data_deidentifier.domain.services.health_check.health_check import (
    HealthCheckService,
)

router = APIRouter()


@router.get("/health", status_code=200, tags=["Health"])
async def health_liveness() -> JSONResponse:
    """Simple liveness check."""
    return JSONResponse(content={"status": "ok", "service": "ddi-api"})


@router.get("/health/ready", tags=["Health"])
async def health_readiness(
    health_service: Annotated[
        HealthCheckService,
        Depends(get_health_check_service),
    ],
) -> JSONResponse:
    """Detailed health check endpoint.

    Returns a 200 OK if all checks pass, otherwise returns appropriate error code.
    """
    result = health_service.check_readiness()

    return JSONResponse(
        status_code=status.HTTP_200_OK
        if result.is_healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ok" if result.is_healthy else "degraded",
            "service": "ddi-api",
            "checks": result.checks,
        },
    )
