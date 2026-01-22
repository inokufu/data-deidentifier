from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from http import HTTPStatus
from logging import DEBUG, getLevelName, getLogger
from time import time
from typing import Any

from fastapi import FastAPI, Request
from logger import LogLevel, LoguruLogger

from data_deidentifier.adapters.infrastructure.config.settings import Settings

from .anonymize.router import router as anonymize_router
from .dependencies import get_engine_factory
from .exception_handler import ExceptionHandler
from .infrastructure.router import router as infra_router
from .pseudonymize.router import router as pseudonymize_router

config = Settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """Lifespan context manager for the FastAPI application.

    Args:
        _app: The FastAPI application instance

    Yields:
        A dictionary containing logger and config objects
    """
    logger = LoguruLogger(level=LogLevel[config.get_log_level().name])
    logger.info(
        "Application starting",
        {
            "app_log_level": config.get_log_level().name,
            "app_env": config.get_environment().name,
        },
    )

    # Pre-load spaCy models and Presidio engines to avoid cold-start latency
    get_engine_factory().warmup(logger=logger)

    yield {"config": config, "logger": logger}

    logger.info("Application shutting down")


app = FastAPI(
    title="Data deidentification API",
    version="0.0.1",
    debug=config.get_log_level() == LogLevel.DEBUG and not config.is_env_production(),
    lifespan=lifespan,
)

exception_handler = ExceptionHandler()
exception_handler.configure(app=app)

app.include_router(router=anonymize_router)
app.include_router(router=pseudonymize_router)
app.include_router(router=infra_router)

# NOTE: Middleware to delete after performance testing
# Disable uvicorn access logger
uvicorn_access = getLogger("uvicorn.access")
uvicorn_access.disabled = True

logger = getLogger("uvicorn")
logger.setLevel(getLevelName(DEBUG))


async def log_request_middleware(request: Request, call_next: Callable) -> Any:  # noqa: ANN401
    """Log request Middleware.

    Args:
        request (Request): The incoming request.
        call_next (_type_): The next middleware or route handler to call

    Returns:
        Any: The response from the next middleware or route handler.
    """
    logger.debug("middleware: log_request_middleware")
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    start_time = time()
    response = await call_next(request)
    process_time = (time() - start_time) * 1000
    fmt_duration = f"{process_time:.2f}"
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    status = response.status_code
    method = request.method
    try:
        phrase = HTTPStatus(status).phrase
    except ValueError:
        phrase = ""
    msg = f'{host}:{port} - "{method} {url}" {status} {phrase} {fmt_duration}ms'
    logger.debug(msg)
    return response


app.middleware("http")(log_request_middleware)
