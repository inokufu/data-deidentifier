from typing import Annotated, Any, override

from configcore import Settings as CoreSettings
from pydantic import BeforeValidator, Field

from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.pseudonymization_method import (
    PseudonymizationMethod,
)

from .contract import ConfigContract


class Settings(CoreSettings, ConfigContract):
    """Application settings loaded from environment variables, via Pydantic model."""

    default_language: Annotated[
        SupportedLanguage,
        BeforeValidator(lambda v: v.lower() if isinstance(v, str) else v),
    ] = Field(default=SupportedLanguage.ENGLISH)

    default_minimum_score: float = Field(default=0.5, ge=0.0, le=1.0)

    default_entity_types: list[str] = Field(default_factory=list)

    default_anonymization_operator: Annotated[
        AnonymizationOperator,
        BeforeValidator(
            lambda v: AnonymizationOperator[v.upper()] if isinstance(v, str) else v,
        ),
    ] = Field(
        default=AnonymizationOperator.REPLACE,
    )

    default_pseudonymization_method: Annotated[
        PseudonymizationMethod,
        BeforeValidator(
            lambda v: PseudonymizationMethod[v.upper()] if isinstance(v, str) else v,
        ),
    ] = Field(
        default=PseudonymizationMethod.RANDOM_NUMBER,
    )

    # Config mappings for entity enrichment (JSON string format), example:
    # {"LOCATION": {"type": "http", "url": "http://geo-service/enrich"}} # noqa: ERA001
    enrichment_configurations: dict[str, dict[str, Any]] = Field(default_factory=dict)

    @override
    def get_default_language(self) -> SupportedLanguage:
        return self.default_language

    @override
    def get_default_minimum_score(self) -> float:
        return self.default_minimum_score

    @override
    def get_default_entity_types(self) -> list[str]:
        return self.default_entity_types

    @override
    def get_default_anonymization_operator(self) -> AnonymizationOperator:
        return self.default_anonymization_operator

    @override
    def get_default_pseudonymization_method(self) -> PseudonymizationMethod:
        return self.default_pseudonymization_method

    @override
    def get_enrichment_configurations(self) -> dict[str, dict[str, Any]]:
        return self.enrichment_configurations
