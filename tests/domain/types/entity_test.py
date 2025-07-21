import pytest

from src.data_deidentifier.domain.types.entity import Entity


class TestEntityCreation:
    """Test entity creation with valid parameters."""

    def test_create_entity_with_required_fields(self) -> None:
        """Should create entity with all required fields."""
        entity = Entity(type="PERSON", start=0, end=4, score=0.95)

        assert entity.type == "PERSON"
        assert entity.start == 0
        assert entity.end == 4
        assert entity.score == 0.95
        assert entity.text is None
        assert entity.path is None

    def test_create_entity_with_all_fields(self) -> None:
        """Should create entity with all fields including optional ones."""
        entity = Entity(
            type="EMAIL_ADDRESS",
            start=10,
            end=24,
            score=0.88,
            text="john@email.com",
            path="user.contact.email",
        )

        assert entity.type == "EMAIL_ADDRESS"
        assert entity.start == 10
        assert entity.end == 24
        assert entity.score == 0.88
        assert entity.text == "john@email.com"
        assert entity.path == "user.contact.email"


class TestEntityPositionValidation:
    """Test entity position validation rules."""

    @pytest.mark.parametrize(
        ("start", "end", "expected_error"),
        [
            (-1, 4, "entity start position cannot be negative: -1"),
            (0, -5, "entity end position cannot be negative: -5"),
            (-2, -1, "entity start position cannot be negative: -2"),
            (
                10,
                5,
                "entity start position \\(10\\) must be less than end position \\(5\\)",
            ),
            (
                5,
                5,
                "entity start position \\(5\\) must be less than end position \\(5\\)",
            ),
        ],
    )
    def test_invalid_positions(self, start: int, end: int, expected_error: str) -> None:
        """Should raise ValueError for invalid start or end."""
        with pytest.raises(ValueError, match=expected_error):
            Entity(type="PERSON", start=start, end=end, score=0.95)


class TestEntityEdgeCases:
    """Test entity edge cases and boundary conditions."""

    def test_zero_positions_valid(self) -> None:
        """Should accept zero positions."""
        entity = Entity(type="PERSON", start=0, end=1, score=0.5)

        assert entity.start == 0
        assert entity.end == 1

    def test_large_positions_valid(self) -> None:
        """Should accept large position values."""
        entity = Entity(type="PERSON", start=1000000, end=1000010, score=0.9)

        assert entity.start == 1000000
        assert entity.end == 1000010

    def test_score_boundary_values(self) -> None:
        """Should accept boundary score values."""
        # Score 0.0
        entity_min = Entity(type="PERSON", start=0, end=1, score=0.0)
        assert entity_min.score == 0.0

        # Score 1.0
        entity_max = Entity(type="PERSON", start=0, end=1, score=1.0)
        assert entity_max.score == 1.0

    def test_empty_string_text_raises_error(self) -> None:
        """Should reject empty string as text."""
        with pytest.raises(ValueError, match="entity text cannot be empty string"):
            Entity(type="PERSON", start=0, end=4, score=0.5, text="")

    def test_empty_string_path_raises_error(self) -> None:
        """Should reject empty string as path."""
        with pytest.raises(ValueError, match="entity path cannot be empty string"):
            Entity(type="PERSON", start=0, end=4, score=0.5, path="")

    def test_invalid_range_raises_error(self) -> None:
        """Should reject empty string as text."""
        with pytest.raises(
            ValueError,
            match="entity text length must match position range",
        ):
            Entity(type="PERSON", text="Hello world", start=0, end=1, score=0.5)

        with pytest.raises(
            ValueError,
            match="entity text length must match position range",
        ):
            Entity(type="PERSON", text="Hello world", start=0, end=42, score=0.5)

    def test_unicode_text(self) -> None:
        """Should handle Unicode characters in text."""
        entity = Entity(type="PERSON", start=0, end=6, score=0.95, text="José 🎭")

        assert entity.text == "José 🎭"

    def test_complex_path_format(self) -> None:
        """Should handle complex path formats."""
        entity = Entity(
            type="EMAIL_ADDRESS",
            start=0,
            end=15,
            score=0.88,
            path="users[0].contacts.emails[1].address",
        )

        assert entity.path == "users[0].contacts.emails[1].address"
