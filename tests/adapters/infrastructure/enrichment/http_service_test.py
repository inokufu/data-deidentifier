from unittest.mock import Mock, patch

import pytest
from logger import LoggerContract

from src.data_deidentifier.adapters.infrastructure.enrichment.http_service import (
    HttpPseudonymEnricher,
)
from src.data_deidentifier.adapters.infrastructure.http.client import (
    BaseHttpClient,
    HttpClientError,
)
from src.data_deidentifier.domain.exceptions import PseudonymEnrichmentError
from src.data_deidentifier.domain.types.entity import Entity


class TestHttpPseudonymEnricherCanHandleEntity:
    """Test can_handle_entity method."""

    def test_can_handle_entity_with_valid_url(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return True when URL is present and is string."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.can_handle_entity(sample_entity)

        # Assert
        assert result is True

    def test_can_handle_entity_with_missing_url(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return False when URL is missing."""
        # Arrange
        params = {"timeout": 30}  # No URL
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.can_handle_entity(sample_entity)

        # Assert
        assert result is False

    def test_can_handle_entity_with_non_string_url(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return False when URL is not a string."""
        # Arrange
        params = {"url": 123}  # Non-string URL
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.can_handle_entity(sample_entity)

        # Assert
        assert result is False


class TestHttpPseudonymEnricherConfigurationMethods:
    """Test configuration getter methods."""

    def test_get_service_url(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return URL from params."""
        # Arrange
        service_url = "http://test-service.com"
        params = {"url": service_url}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_service_url(sample_entity)

        # Assert
        assert result == service_url

    def test_get_http_method_default(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return POST as default HTTP method."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_http_method()

        # Assert
        assert result == "POST"

    def test_get_http_method_custom(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return custom HTTP method when specified."""
        # Arrange
        custom_method = "GET"
        params = {"url": "http://example.com", "http_method": custom_method}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_http_method()

        # Assert
        assert result == custom_method

    def test_get_timeout_seconds_default(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return default timeout when not specified."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_timeout_seconds()

        # Assert
        assert result == BaseHttpClient.DEFAULT_TIMEOUT

    def test_get_timeout_seconds_custom(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return custom timeout when specified."""
        # Arrange
        custom_timeout = 60
        params = {"url": "http://example.com", "timeout": custom_timeout}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_timeout_seconds()

        # Assert
        assert result == custom_timeout

    def test_get_timeout_seconds_bounds_validation(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should validate timeout bounds (1-300 seconds)."""
        # Arrange - Test lower bound
        params_low = {"url": "http://example.com", "timeout": -5}
        enricher_low = HttpPseudonymEnricher(params=params_low, logger=mock_logger)

        # Test upper bound
        params_high = {"url": "http://example.com", "timeout": 500}
        enricher_high = HttpPseudonymEnricher(params=params_high, logger=mock_logger)

        # Act
        result_low = enricher_low.get_timeout_seconds()
        result_high = enricher_high.get_timeout_seconds()

        # Assert
        assert result_low == 1  # Minimum bound
        assert result_high == 300  # Maximum bound

    def test_get_timeout_seconds_invalid_type_uses_default(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should use default timeout when type is invalid."""
        # Arrange
        params = {"url": "http://example.com", "timeout": "invalid"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_timeout_seconds()

        # Assert
        assert result == BaseHttpClient.DEFAULT_TIMEOUT

    def test_get_request_headers(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return JSON content-type headers."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_request_headers()

        # Assert
        assert result == {"Content-Type": "application/json"}

    def test_get_request_key_default(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return 'text' as default request key."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_request_key()

        # Assert
        assert result == "text"

    def test_get_request_key_custom(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return custom request key when specified."""
        # Arrange
        request_key = "input"
        params = {"url": "http://example.com", "request_key": request_key}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_request_key()

        # Assert
        assert result == request_key

    def test_get_response_key_default(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return 'text' as default response key."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_response_key()

        # Assert
        assert result == "text"

    def test_get_response_key_custom(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return custom response key when specified."""
        # Arrange
        response_key = "result"
        params = {"url": "http://example.com", "response_key": response_key}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_response_key()

        # Assert
        assert result == response_key


class TestHttpPseudonymEnricherRequestBuilding:
    """Test request building and response parsing methods."""

    def test_build_request_data_default_key(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should build request data with default key."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.build_request_data(sample_entity)

        # Assert
        assert result == {"text": sample_entity.text}

    def test_build_request_data_custom_key(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should build request data with custom key."""
        # Arrange
        request_key = "input_text"
        params = {"url": "http://example.com", "request_key": request_key}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.build_request_data(sample_entity)

        # Assert
        assert result == {request_key: sample_entity.text}

    def test_parse_response_data_default_key(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should parse response data with default key."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)
        response_data = {"text": "enriched_value", "other": "data"}

        # Act
        result = enricher.parse_response_data(response_data)

        # Assert
        assert result == "enriched_value"

    def test_parse_response_data_custom_key(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should parse response data with custom key."""
        # Arrange
        response_key = "enrichment"
        custom_value = "custom_value"
        params = {"url": "http://example.com", "response_key": response_key}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)
        response_data = {response_key: custom_value, "text": "other"}

        # Act
        result = enricher.parse_response_data(response_data)

        # Assert
        assert result == custom_value

    def test_parse_response_data_missing_key_returns_none(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return None when response key is missing."""
        # Arrange
        params = {"url": "http://example.com", "response_key": "missing"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)
        response_data = {"text": "value"}

        # Act
        result = enricher.parse_response_data(response_data)

        # Assert
        assert result is None


class TestHttpPseudonymEnricherGetEnrichment:
    """Test get_enrichment method."""

    def test_get_enrichment_success(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return enrichment when HTTP request succeeds."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        mock_response = Mock()
        mock_response.json.return_value = {"text": "enriched_location"}

        # Act
        with patch.object(enricher.http_client, "request", return_value=mock_response):
            result = enricher.get_enrichment(sample_entity)

        # Assert
        assert result == "enriched_location"

    def test_get_enrichment_cannot_handle_entity_returns_none(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return None when entity cannot be handled."""
        # Arrange
        params = {}  # No URL, so can_handle_entity returns False
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        # Act
        result = enricher.get_enrichment(sample_entity)

        # Assert
        assert result is None

    @pytest.mark.parametrize(
        "response_data",
        [
            {"text": ""},  # Empty string
            {"text": "   "},  # Whitespace only
            {"text": None},  # None value
            {},  # Missing key
        ],
    )
    def test_get_enrichment_empty_enrichment_returns_none(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
        response_data: dict,
    ) -> None:
        """Should return None when enrichment is empty or whitespace."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        mock_response = Mock()
        mock_response.json.return_value = response_data

        # Act
        with patch.object(enricher.http_client, "request", return_value=mock_response):
            result = enricher.get_enrichment(sample_entity)

        # Assert
        assert result is None

    def test_get_enrichment_http_client_error_raises_enrichment_error(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise PseudonymEnrichmentError when HTTP client fails."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        http_error = HttpClientError("HTTP request failed")

        # Act & Assert
        with (
            patch.object(enricher.http_client, "request", side_effect=http_error),
            pytest.raises(PseudonymEnrichmentError),
        ):
            enricher.get_enrichment(sample_entity)

    def test_get_enrichment_json_error_raises_enrichment_error(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise PseudonymEnrichmentError when JSON parsing fails."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")

        # Act & Assert
        with (
            patch.object(enricher.http_client, "request", return_value=mock_response),
            pytest.raises(PseudonymEnrichmentError),
        ):
            enricher.get_enrichment(sample_entity)

    def test_get_enrichment_logs_debug_messages(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should log appropriate debug messages during enrichment."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        enriched_value = "enriched_value"
        mock_response = Mock()
        mock_response.json.return_value = {"text": enriched_value}

        # Act
        with patch.object(enricher.http_client, "request", return_value=mock_response):
            enricher.get_enrichment(sample_entity)

        # Assert
        mock_logger.debug.assert_any_call(
            "Starting pseudonym enrichment via HTTP",
            {"entity_type": sample_entity.type},
        )
        mock_logger.debug.assert_any_call(
            "Pseudonym enrichment successful",
            {"enrichment": enriched_value},
        )

    def test_get_enrichment_logs_warning_on_exception(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should log warning when exception occurs during processing."""
        # Arrange
        params = {"url": "http://example.com"}
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        mock_response = Mock()
        mock_response.json.side_effect = ValueError("JSON error")

        # Act & Assert
        with (
            patch.object(enricher.http_client, "request", return_value=mock_response),
            pytest.raises(PseudonymEnrichmentError),
        ):
            enricher.get_enrichment(sample_entity)

        mock_logger.warning.assert_called_once_with(
            "Pseudonym enrichment processing failed",
            {"error": "JSON error", "entity_type": sample_entity.type},
        )


class TestHttpPseudonymEnricherIntegration:
    """Test integration scenarios."""

    def test_get_enrichment_with_custom_configuration(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle custom configuration parameters."""
        # Arrange
        custom_url = "http://custom-service.com/enrich"
        custom_timeout = 45
        request_key = "input_text"
        response_key = "enriched_text"
        http_method = "GET"
        enrichment_result = "custom_enrichment"

        params = {
            "url": custom_url,
            "timeout": custom_timeout,
            "request_key": request_key,
            "response_key": response_key,
            "http_method": http_method,
        }
        enricher = HttpPseudonymEnricher(params=params, logger=mock_logger)

        mock_response = Mock()
        mock_response.json.return_value = {response_key: enrichment_result}

        # Act
        with patch.object(
            enricher.http_client,
            "request",
            return_value=mock_response,
        ) as mock_request:
            result = enricher.get_enrichment(sample_entity)

        # Assert
        assert result == enrichment_result
        mock_request.assert_called_once_with(
            url=custom_url,
            method=http_method,
            data={request_key: sample_entity.text},
            headers={"Content-Type": "application/json"},
            timeout_seconds=custom_timeout,
        )
