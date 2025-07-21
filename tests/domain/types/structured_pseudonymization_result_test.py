from src.data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)
from src.data_deidentifier.domain.types.structured_pseudonymization_result import (
    StructuredDataPseudonymizationResult,
)


class TestStructuredDataPseudonymizationResult:
    """Test StructuredDataPseudonymizationResult dataclass."""

    def test_create_result_with_empty_fields(self) -> None:
        """Should create result with empty detected fields."""
        data = {"name": "Hello world", "age": 30}

        result = StructuredDataPseudonymizationResult(
            pseudonymized_data=data,
            detected_fields=[],
        )

        assert result.pseudonymized_data == data
        assert result.detected_fields == []
        assert result.field_mapping == {}

    def test_create_result_with_detected_fields(self) -> None:
        """Should create result with detected fields."""
        data = {"name": "<PERSON_1>", "email": "<EMAIL_ADDRESS_1>", "age": 30}
        fields = [
            StructuredDataAnalysisField("name", "PERSON"),
            StructuredDataAnalysisField("email", "EMAIL_ADDRESS"),
        ]

        result = StructuredDataPseudonymizationResult(
            pseudonymized_data=data,
            detected_fields=fields,
        )

        assert result.pseudonymized_data == data
        assert len(result.detected_fields) == 2
        assert result.detected_fields[0].field_name == "name"
        assert result.detected_fields[1].field_name == "email"

    def test_field_mapping_property(self) -> None:
        """Should generate correct field mapping dictionary."""
        fields = [
            StructuredDataAnalysisField("user.name", "PERSON"),
            StructuredDataAnalysisField("user.email", "EMAIL_ADDRESS"),
            StructuredDataAnalysisField("user.address", "LOCATION"),
        ]

        result = StructuredDataPseudonymizationResult(
            pseudonymized_data={
                "user": {
                    "name": "<PERSON_1>",
                    "email": "<EMAIL_ADDRESS_1>",
                    "address": "<LOCATION_1>",
                },
            },
            detected_fields=fields,
        )

        expected_mapping = {
            "user.name": "PERSON",
            "user.email": "EMAIL_ADDRESS",
            "user.address": "LOCATION",
        }

        assert result.field_mapping == expected_mapping

    def test_nested_data_structure(self) -> None:
        """Should handle nested data structures."""
        data = {
            "user": {
                "name": "<PERSON_1>",
                "contact": {"email": "<EMAIL_ADDRESS_1>", "phone": "<PHONE_NUMBER>"},
            },
            "metadata": {"version": "1.0"},
        }

        fields = [
            StructuredDataAnalysisField("user.name", "PERSON"),
            StructuredDataAnalysisField("user.contact.email", "EMAIL_ADDRESS"),
            StructuredDataAnalysisField("user.contact.phone", "PHONE_NUMBER"),
        ]

        result = StructuredDataPseudonymizationResult(
            pseudonymized_data=data,
            detected_fields=fields,
        )

        assert result.pseudonymized_data == data
        assert len(result.detected_fields) == 3
        assert result.field_mapping["user.name"] == "PERSON"
        assert result.field_mapping["user.contact.email"] == "EMAIL_ADDRESS"
