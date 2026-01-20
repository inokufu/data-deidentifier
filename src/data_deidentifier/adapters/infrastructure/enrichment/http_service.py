from typing import Any, override

from logger import LoggerContract

from data_deidentifier.adapters.infrastructure.http.client import (
    BaseHttpClient,
    HttpClientError,
)
from data_deidentifier.domain.contracts.enricher.enricher import (
    PseudonymEnricherContract,
)
from data_deidentifier.domain.exceptions import PseudonymEnrichmentError
from data_deidentifier.domain.types.entity import Entity


class HttpPseudonymEnricher(PseudonymEnricherContract):
    """HTTP client specifically for entity enrichment services.

    Provides a higher-level interface for making enrichment requests by wrapping
    the base HTTP client with enrichment-specific logic and error handling.

    This class implements the Template Method pattern where get_enrichment()
    orchestrates the enrichment process, while specific methods can be overridden
    by subclasses for customization.

    Attributes:
        PARAM_URL: Parameter key for the service URL.
        PARAM_TIMEOUT: Parameter key for request timeout.
        PARAM_REQUEST_KEY: Parameter key for the JSON request field name.
        PARAM_RESPONSE_KEY: Parameter key for the JSON response field name.
        PARAM_HTTP_METHOD: Parameter key for the HTTP method.
    """

    PARAM_URL = "url"
    PARAM_TIMEOUT = "timeout"
    PARAM_REQUEST_KEY = "request_key"
    PARAM_RESPONSE_KEY = "response_key"
    PARAM_HTTP_METHOD = "http_method"

    @override
    def __init__(self, params: dict[str, Any], logger: LoggerContract) -> None:
        super().__init__(params=params, logger=logger)

        self.http_client = BaseHttpClient(logger)

    @override
    def get_enrichment(self, entity: Entity) -> str | None:
        if not self.can_handle_entity(entity):
            return None

        logger_context = {"entity_type": entity.type}
        self.logger.debug("Starting pseudonym enrichment via HTTP", logger_context)

        try:
            response = self.http_client.request(
                url=self.get_service_url(entity),
                method=self.get_http_method(),
                data=self.build_request_data(entity=entity),
                headers=self.get_request_headers(),
                timeout_seconds=self.get_timeout_seconds(),
            )

            enrichment = self.parse_response_data(response_data=response.json())

            if enrichment and isinstance(enrichment, str) and enrichment.strip():
                self.logger.debug(
                    "Pseudonym enrichment successful",
                    {"enrichment": enrichment},
                )
                return enrichment

            self.logger.debug("No enrichment returned by service", logger_context)

        except HttpClientError as e:
            # Transform generic HTTP error into enrichment-specific context
            raise PseudonymEnrichmentError from e
        except Exception as e:
            # Handle JSON parsing errors, etc.
            self.logger.warning(
                "Pseudonym enrichment processing failed",
                {"error": str(e), **logger_context},
            )
            raise PseudonymEnrichmentError from e

        return None

    def can_handle_entity(self, _entity: Entity) -> bool:
        """Check if this enricher can handle the given entity.

        Args:
            _entity: The entity to check.

        Returns:
            True if the entity can be handled, False otherwise.
        """
        return self.PARAM_URL in self.params and isinstance(
            self.params.get(self.PARAM_URL),
            str,
        )

    def get_service_url(self, _entity: Entity) -> str:
        """Get the service URL for the enrichment request.

        Args:
            _entity: The entity being enriched.

        Returns:
            The service URL.
        """
        url = self.params.get(self.PARAM_URL)
        if not isinstance(url, str):
            raise TypeError("Service URL must be configured as a string")
        return url

    def get_http_method(self) -> str:
        """Get the HTTP method for the enrichment request.

        Returns:
            The HTTP method (defaults to "POST").
        """
        return self.params.get(self.PARAM_HTTP_METHOD, "POST")

    def get_timeout_seconds(self) -> int:
        """Get the request timeout in seconds.

        Validates and bounds the timeout value between 1 and 300 seconds.

        Returns:
            The timeout value in seconds.
        """
        timeout = self.params.get(self.PARAM_TIMEOUT, BaseHttpClient.DEFAULT_TIMEOUT)
        if not isinstance(timeout, int):
            timeout = BaseHttpClient.DEFAULT_TIMEOUT
        return max(1, min(timeout, 300))

    def get_request_headers(self) -> dict[str, str]:
        """Get the HTTP headers for the enrichment request.

        Returns:
            Dictionary of HTTP headers.
        """
        return {"Content-Type": "application/json"}

    def get_request_key(self) -> str:
        """Get the JSON key for sending the entity text in the request.

        Returns:
            The JSON key name (defaults to "text").
        """
        return self.params.get(self.PARAM_REQUEST_KEY, "text")

    def get_response_key(self) -> str:
        """Get the JSON key for extracting enrichment from the response.

        Returns:
            The JSON key name (defaults to "text").
        """
        return self.params.get(self.PARAM_RESPONSE_KEY, "text")

    def build_request_data(self, entity: Entity) -> dict[str, Any]:
        """Build the request data payload.

        Creates a dictionary with the entity text using the configured request key.

        Args:
            entity: The entity being enriched.

        Returns:
            Dictionary containing the request data.
        """
        return {self.get_request_key(): entity.text}

    def parse_response_data(self, response_data: dict[str, Any]) -> str | None:
        """Parse the HTTP response to extract enrichment data.

        Extracts the enrichment value from the response using the configured key.

        Args:
            response_data: The JSON response data from the service.

        Returns:
            The extracted enrichment string, or None if not found.
        """
        return response_data.get(self.get_response_key())
