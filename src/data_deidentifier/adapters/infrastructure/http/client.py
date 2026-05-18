from typing import Any

import httpx
from fastapi import status
from httpx import HTTPError, HTTPStatusError, Response
from logger import LoggerContract
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)


class HttpClientError(Exception):
    """Generic HTTP client error for BaseHttpClient.

    This exception is raised by the BaseHttpClient when HTTP operations fail.
    It provides a generic error type that can be caught and transformed by
    specialized clients into more specific exceptions.
    """


class BaseHttpClient:
    """Base HTTP client with retry logic and exponential backoff.

    Provides common HTTP request handling with automatic retries for server errors,
    exponential backoff, and comprehensive logging.
    """

    DEFAULT_TIMEOUT = 10

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the HTTP client.

        Args:
            logger: Logger instance for recording HTTP operations and errors
        """
        self.logger = logger

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception(lambda e: BaseHttpClient._should_retry(e)),  # noqa: PLW0108
        reraise=True,
    )
    def request(
        self,
        url: str,
        method: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT,
    ) -> Response:
        """Make an HTTP request with retry logic.

        Sends an HTTP request with the specified method and data. Automatically
        retries on server errors (5xx) with exponential backoff.

        Args:
            url: Complete URL for the request
            method: HTTP method to use (GET, POST, PUT, etc.)
            data: Request payload data
            headers: Optional HTTP headers to include in the request
            timeout_seconds: Request timeout in seconds. If None, uses config default

        Returns:
            Response: The HTTP response from the service.

        Raises:
            HttpClientError: If the request fails after all retries or
                returns a non-2xx status code.

        Note:
            Only server errors (5xx) are retried. Client errors (4xx) indicate
            invalid requests and are not retried.
        """
        logger_context = {
            "url": url,
            "method": method,
            "timeout_seconds": timeout_seconds,
        }
        self.logger.debug("Making HTTP request", logger_context)

        try:
            with httpx.Client() as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=data if method in ("POST", "PUT", "PATCH") else None,
                    params=data if method == "GET" else None,
                    headers=headers,
                    timeout=timeout_seconds,
                )
                response.raise_for_status()
        except HTTPError as e:
            msg = "HTTP error occurred"
            self.logger.exception(msg, e, logger_context)
            raise HttpClientError(msg) from e

        self.logger.debug(
            "HTTP request successful",
            {
                "url": url,
                "status_code": response.status_code,
                "response_size": len(response.text),
            },
        )
        return response

    @classmethod
    def _should_retry(cls, exception: BaseException) -> bool:
        """Determine if an exception should trigger a retry.

        Args:
            exception: The exception that occurred during the HTTP request.

        Returns:
            bool: True if the exception is a server error (5xx) that should be
                retried, False otherwise.
        """
        cause = exception.__cause__
        return (
            isinstance(cause, HTTPStatusError)
            and cause.response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR
        )
