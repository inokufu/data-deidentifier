from unittest.mock import Mock, patch

import pytest
from logger import LoggerContract

from src.data_deidentifier.adapters.infrastructure.config.contract import ConfigContract
from src.data_deidentifier.adapters.infrastructure.enrichment.factory import (
    EnrichmentFactory,
)
from src.data_deidentifier.adapters.infrastructure.enrichment.http_service import (
    HttpPseudonymEnricher,
)
from src.data_deidentifier.domain.contracts.enricher.enricher import (
    PseudonymEnricherContract,
)
from src.data_deidentifier.domain.exceptions import PseudonymEnrichmentError


class TestEnrichmentFactoryGetEnricherForEntity:
    """Test get_enricher_for_entity method."""

    def test_get_enricher_for_entity_success(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return enricher when entity type is configured."""
        # Arrange
        mock_config.get_enrichment_configurations.return_value = {
            "LOCATION": {"type": "http", "url": "http://example.com"},
        }

        mock_enricher = Mock(spec=PseudonymEnricherContract)

        factory = EnrichmentFactory(config=mock_config, logger=mock_logger)

        # Act
        with patch.object(EnrichmentFactory, "create", return_value=mock_enricher):
            result = factory.get_enricher_for_entity("LOCATION")

        # Assert
        assert result == mock_enricher

    def test_get_enricher_for_entity_not_configured_returns_none(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return None when entity type is not configured."""
        # Arrange
        mock_config.get_enrichment_configurations.return_value = {
            "LOCATION": {"type": "http", "url": "http://example.com"},
        }

        factory = EnrichmentFactory(config=mock_config, logger=mock_logger)

        # Act
        result = factory.get_enricher_for_entity("PERSON")

        # Assert
        assert result is None

    def test_get_enricher_for_entity_empty_config_returns_none(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return None when enrichment configurations are empty."""
        # Arrange
        mock_config.get_enrichment_configurations.return_value = {}

        factory = EnrichmentFactory(config=mock_config, logger=mock_logger)

        # Act
        result = factory.get_enricher_for_entity("LOCATION")

        # Assert
        assert result is None

    def test_get_enricher_for_entity_create_error_logs_and_reraises(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
    ) -> None:
        """Should log exception and re-raise when create fails."""
        # Arrange
        mock_config.get_enrichment_configurations.return_value = {
            "LOCATION": {"type": "invalid"},
        }

        factory = EnrichmentFactory(config=mock_config, logger=mock_logger)
        create_error = PseudonymEnrichmentError("Invalid config")

        # Act & Assert
        with (
            pytest.raises(PseudonymEnrichmentError, match="Invalid config"),
            patch.object(EnrichmentFactory, "create", side_effect=create_error),
        ):
            factory.get_enricher_for_entity("LOCATION")

        mock_logger.exception.assert_called_once_with("Enrichment error", create_error)


class TestEnrichmentFactoryCreate:
    """Test create classmethod."""

    def test_create_http_enricher_success(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create HttpPseudonymEnricher for HTTP type."""
        # Arrange
        enrichment_config = {
            "type": "http",
            "url": "http://geo-service/enrich",
            "timeout": 30,
        }

        # Act
        result = EnrichmentFactory.create(
            entity_type="LOCATION",
            enrichment_config=enrichment_config,
            logger=mock_logger,
        )

        # Assert
        assert result is not None
        assert isinstance(result, HttpPseudonymEnricher)

    def test_create_case_insensitive_type(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle case-insensitive enrichment type."""
        # Arrange
        enrichment_config = {
            "type": "HTTP",  # Uppercase
            "url": "http://example.com",
        }

        # Act
        result = EnrichmentFactory.create(
            entity_type="LOCATION",
            enrichment_config=enrichment_config,
            logger=mock_logger,
        )

        # Assert
        assert result is not None

    def test_create_missing_type_raises_error(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise error when 'type' is missing from config."""
        # Arrange
        enrichment_config = {"url": "http://example.com"}

        # Act & Assert
        with pytest.raises(
            PseudonymEnrichmentError,
            match="Missing 'type' in enrichment config for entity type 'LOCATION'",
        ):
            EnrichmentFactory.create(
                entity_type="LOCATION",
                enrichment_config=enrichment_config,
                logger=mock_logger,
            )

    def test_create_empty_type_raises_error(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise error when 'type' is empty."""
        # Arrange
        enrichment_config = {"type": "", "url": "http://example.com"}

        # Act & Assert
        with pytest.raises(
            PseudonymEnrichmentError,
            match="Missing 'type' in enrichment config for entity type 'LOCATION'",
        ):
            EnrichmentFactory.create(
                entity_type="LOCATION",
                enrichment_config=enrichment_config,
                logger=mock_logger,
            )

    def test_create_invalid_type_raises_error(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise error for invalid enrichment type."""
        # Arrange
        enrichment_config = {"type": "invalid_type", "url": "http://example.com"}

        # Act & Assert
        with pytest.raises(
            PseudonymEnrichmentError,
            match="Unsupported enrichment type",
        ):
            EnrichmentFactory.create(
                entity_type="LOCATION",
                enrichment_config=enrichment_config,
                logger=mock_logger,
            )


class TestEnrichmentFactoryIntegration:
    """Test factory integration scenarios."""

    def test_full_flow_get_enricher_for_entity(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle full flow from get_enricher_for_entity to create."""
        # Arrange
        mock_config.get_enrichment_configurations.return_value = {
            "LOCATION": {
                "type": "http",
                "url": "http://geo-service/enrich",
                "timeout": 30,
            },
        }

        factory = EnrichmentFactory(config=mock_config, logger=mock_logger)

        # Act
        result = factory.get_enricher_for_entity("LOCATION")

        # Assert
        assert result is not None
        assert isinstance(result, HttpPseudonymEnricher)

    def test_multiple_entity_types_configuration(
        self,
        mock_config: ConfigContract,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle multiple entity types with different configs."""
        # Arrange
        mock_config.get_enrichment_configurations.return_value = {
            "LOCATION": {"type": "http", "url": "http://geo-service/enrich"},
            "PERSON": {"type": "http", "url": "http://people-service/enrich"},
            "ORG": {"type": "http", "url": "http://org-service/enrich"},
        }

        factory = EnrichmentFactory(config=mock_config, logger=mock_logger)

        # Act
        result_location = factory.get_enricher_for_entity("LOCATION")
        result_person = factory.get_enricher_for_entity("PERSON")
        result_org = factory.get_enricher_for_entity("ORG")
        result_unknown = factory.get_enricher_for_entity("EMAIL")

        # Assert
        assert result_location is not None
        assert result_person is not None
        assert result_org is not None
        assert result_unknown is None


class TestEnrichmentFactoryGetSupportedTypes:
    """Test get_supported_types classmethod."""

    def test_get_supported_types_returns_expected_types(self) -> None:
        """Should return expected enrichment types."""
        # Act
        supported_types = EnrichmentFactory.get_supported_types()

        # Assert
        assert len(supported_types) > 0
