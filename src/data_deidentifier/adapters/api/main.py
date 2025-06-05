from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from logger import LogLevel, LoguruLogger

from src.data_deidentifier.adapters.infrastructure.config.settings import Settings

from .analyze.router import router as analyze_router
from .anonymize.router import router as anonymize_router
from .exception_handler import ExceptionHandler

config = Settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """Lifespan context manager for the FastAPI application.

    Args:
        _app: The FastAPI application instance

    Yields:
        A dictionary containing logger and config objects
    """
    logger = LoguruLogger(level=config.get_log_level())
    logger.info(
        "Application starting",
        {
            "app_log_level": config.get_log_level().name,
            "app_env": config.get_environment().name,
        },
    )

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

app.include_router(router=analyze_router)
app.include_router(router=anonymize_router)
