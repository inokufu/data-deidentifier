from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from importlib.metadata import version
from typing import Any

from fastapi import FastAPI
from logger import LogLevel, LoguruLogger
from observability import build_sentry_monitoring

from data_deidentifier.adapters.infrastructure.config.settings import Settings

from .anonymize.router import router as anonymize_router
from .dependencies import get_engine_factory
from .exception_handler import ExceptionHandler
from .infrastructure.router import router as infra_router
from .pseudonymize.router import router as pseudonymize_router

config = Settings()
release = version("data_deidentifier")
monitoring = build_sentry_monitoring(
    service_name="data-deidentifier",
    environment=config.get_environment().name.lower(),
    release=release,
    dsn=config.get_monitoring_dsn(),
    untraced_paths=["/health", "/health/ready"],
)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[dict[str, Any]]:
    """Lifespan context manager for the FastAPI application.

    Args:
        _app: The FastAPI application instance

    Yields:
        A dictionary containing logger, config and monitoring objects
    """
    logger = LoguruLogger(level=LogLevel[config.get_log_level().name])
    logger.info(
        "Application starting",
        {
            "app_log_level": config.get_log_level().name,
            "app_env": config.get_environment().name,
        },
    )

    # Pre-load Nlp models to avoid cold-start latency
    get_engine_factory().warmup(logger=logger)

    yield {"config": config, "logger": logger, "monitoring": monitoring}

    logger.info("Application shutting down")
    monitoring.shutdown()


app = FastAPI(
    title="Data deidentification API",
    version=release,
    debug=config.get_log_level() == LogLevel.DEBUG and not config.is_env_production(),
    lifespan=lifespan,
)

monitoring.instrument_app(app=app)

exception_handler = ExceptionHandler()
exception_handler.configure(app=app)

app.include_router(router=anonymize_router)
app.include_router(router=pseudonymize_router)
app.include_router(router=infra_router)
