from typing import override

from src.data_deidentifier.domain.contracts.mapper import (
    EntityMapperContract,
    StructuredFieldMapperContract,
)
from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisField,
)

from .response import EntityResponse, StructuredFieldResponse


class ApiEntityMapper(EntityMapperContract[EntityResponse]):
    """Implementation of the presentation mapper contract for REST API.

    This class converts between domain entities and API response models,
    ensuring proper data formatting for external API communication.
    """

    @staticmethod
    @override
    def domain_to_adapter(entity: Entity) -> EntityResponse:
        return EntityResponse(
            type=entity.type,
            start=entity.start,
            end=entity.end,
            score=entity.score,
            text=entity.text,
            path=entity.path,
        )

    @staticmethod
    @override
    def adapter_to_domain(entity_response: EntityResponse) -> Entity:
        return Entity(
            type=entity_response.type,
            start=entity_response.start,
            end=entity_response.end,
            score=entity_response.score,
            text=entity_response.text,
            path=entity_response.path,
        )


class ApiStructuredDataMapper(StructuredFieldMapperContract[StructuredFieldResponse]):
    """Implementation of the structured field mapper contract for REST API.

    This class converts between domain structured fields and API response models,
    ensuring proper data formatting for external API communication.
    """

    @staticmethod
    @override
    def domain_to_adapter(
        field: StructuredDataAnalysisField,
    ) -> StructuredFieldResponse:
        return StructuredFieldResponse(
            field_name=field.field_name,
            entity_type=field.entity_type,
        )

    @staticmethod
    @override
    def adapter_to_domain(
        field_response: StructuredFieldResponse,
    ) -> StructuredDataAnalysisField:
        return StructuredDataAnalysisField(
            field_name=field_response.field_name,
            entity_type=field_response.entity_type,
        )
