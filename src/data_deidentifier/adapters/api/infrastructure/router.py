from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse

from src.data_deidentifier.adapters.api.dependencies import get_health_check_service
from src.data_deidentifier.domain.services.health_check.health_check import (
    HealthCheckService,
)

router = APIRouter()


@router.get("/health", status_code=200, tags=["Health"])
async def health_check(
    request: Request,
    health_service: Annotated[
        HealthCheckService,
        Depends(get_health_check_service),
    ],
) -> JSONResponse:
    """Detailed health check endpoint.

    Returns a 200 OK if all checks pass, otherwise returns appropriate error code.
    """
    result = health_service.check_readiness()

    status_code = (
        status.HTTP_200_OK if result.is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    health_data = {
        "status": "ok" if result.is_healthy else "degraded",
        "service": "ddi-api",
        "checks": {
            "env": {
                "log_level": request.state.config.get_log_level().name,
                "env": request.state.config.get_environment().name,
            },
            **result.checks,
        },
    }

    return JSONResponse(
        status_code=status_code,
        content=health_data,
    )
