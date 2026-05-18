from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from logger import LogLevel

from data_deidentifier.domain.exceptions import (
    AnonymizationError,
    DataDeidentifierError,
    EntityTypeValidationError,
    InvalidInputDataError,
    InvalidInputTextError,
    PseudonymizationError,
    UnsupportedStructuredDataError,
)


class ExceptionHandler:
    """A handler for managing and configuring FastAPI exception handling.

    This class provides a centralized way to handle different types of exceptions
    in a FastAPI application, mapping them to appropriate HTTP status codes and
    providing consistent error response formatting.

    The handler supports both known exceptions (configured via error_mapping)
    and unexpected exceptions through a global handler.
    """

    def __init__(self) -> None:
        """Initialize the exception handler with default error mappings."""
        self.error_mapping: dict[type[Exception], int] = {
            ValueError: status.HTTP_400_BAD_REQUEST,
            TypeError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            AnonymizationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DataDeidentifierError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            EntityTypeValidationError: status.HTTP_400_BAD_REQUEST,
            InvalidInputDataError: status.HTTP_400_BAD_REQUEST,
            InvalidInputTextError: status.HTTP_400_BAD_REQUEST,
            PseudonymizationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            UnsupportedStructuredDataError: status.HTTP_400_BAD_REQUEST,
        }

    def configure(self, app: FastAPI) -> None:
        """Configure exception handlers for the FastAPI application.

        Args:
            app: The FastAPI application instance
        """
        # Configure the known_exception_handler for all custom exceptions
        for exception in self.error_mapping:
            app.add_exception_handler(
                exc_class_or_status_code=exception,
                handler=self.known_exception_handler,
            )

        # Add a catch-all handler for any unhandled exceptions
        app.add_exception_handler(
            exc_class_or_status_code=Exception,
            handler=self.global_exception_handler,
        )

    async def known_exception_handler(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle known exceptions and return appropriate JSON responses.

        Args:
            request: The request that caused the exception
            exc: The exception that was raised

        Returns:
            A JSON response containing error details
        """
        status_code = self.error_mapping.get(
            type(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        return JSONResponse(
            status_code=status_code,
            content=self.get_error_detail(
                exc=exc,
                status_code=status_code,
                request=request,
            ),
        )

    async def global_exception_handler(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Global exception handler for unhandled exceptions.

        Args:
            request: The request that caused the exception
            exc: The unhandled exception

        Returns:
            A JSON response indicating an internal server error
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self.get_error_detail(
                exc=exc,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                request=request,
            ),
        )

    @staticmethod
    def get_error_detail(
        exc: Exception,
        status_code: int,
        request: Request,
    ) -> dict[str, str]:
        """Generate an error detail dictionary.

        Based on the exception, status code, and environment.

        In production, internal server errors are given a generic message.

        Args:
            exc: The exception that was raised
            status_code: The HTTP status code associated with the error
            request: The request that caused the exception

        Returns:
            A dictionary containing the error detail
        """
        if (
            request.state.config.is_env_production()
            and status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ):
            return {"detail": "An internal server error occurred."}

        details = {"detail": str(exc)}
        if exc.__cause__ is not None:
            details["cause"] = str(exc.__cause__)

        request.state.logger.exception(
            "HTTP Error",
            exc,
            {
                "status_code": status_code,
                "details": (
                    details
                    if request.state.config.get_log_level() == LogLevel.DEBUG
                    else None
                ),
            },
        )

        return details
