from src.data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
    StructuredDataAnonymizationResult,
)


class TestStructuredDataAnalysisField:
    """Test StructuredDataAnalysisField dataclass."""

    def test_create_field_nested_path(self) -> None:
        """Should create field with nested path notation."""
        field = StructuredDataAnalysisField(
            field_name="user.contact.email",
            entity_type="EMAIL_ADDRESS",
        )

        assert field.field_name == "user.contact.email"
        assert field.entity_type == "EMAIL_ADDRESS"


class TestStructuredDataAnonymizationResult:
    """Test StructuredDataAnonymizationResult dataclass."""

    def test_create_result_with_empty_fields(self) -> None:
        """Should create result with empty detected fields."""
        data = {"name": "Hello world", "age": 30}

        result = StructuredDataAnonymizationResult(
            anonymized_data=data,
            detected_fields=[],
        )

        assert result.anonymized_data == data
        assert result.detected_fields == []
        assert result.field_mapping == {}

    def test_create_result_with_detected_fields(self) -> None:
        """Should create result with detected fields."""
        data = {"name": "******", "email": "********", "age": 30}
        fields = [
            StructuredDataAnalysisField("name", "PERSON"),
            StructuredDataAnalysisField("email", "EMAIL_ADDRESS"),
        ]

        result = StructuredDataAnonymizationResult(
            anonymized_data=data,
            detected_fields=fields,
        )

        assert result.anonymized_data == data
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

        result = StructuredDataAnonymizationResult(
            anonymized_data={
                "user": {"name": "******", "email": "********", "address": "*******"},
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
                "name": "*******",
                "contact": {"email": "*********", "phone": "*******"},
            },
            "metadata": {"version": "1.0"},
        }

        fields = [
            StructuredDataAnalysisField("user.name", "PERSON"),
            StructuredDataAnalysisField("user.contact.email", "EMAIL_ADDRESS"),
            StructuredDataAnalysisField("user.contact.phone", "PHONE_NUMBER"),
        ]

        result = StructuredDataAnonymizationResult(
            anonymized_data=data,
            detected_fields=fields,
        )

        assert result.anonymized_data == data
        assert len(result.detected_fields) == 3
        assert result.field_mapping["user.name"] == "PERSON"
        assert result.field_mapping["user.contact.email"] == "EMAIL_ADDRESS"
