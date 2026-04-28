import pytest

from data_deidentifier.adapters.presidio.json_utils import flatten, unflatten


class TestFlatten:
    """Tests for the flatten function."""

    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            ({"a": "x"}, {"a": "x"}),
            ({"a": {"b": "x"}}, {"a": {"b": "x"}}),
            ({"a": {"b": {"c": "x"}}}, {"a": {"b": {"c": "x"}}}),
            (["x", "y"], {"0": "x", "1": "y"}),
            ([{"a": "x"}, {"a": "y"}], {"0": {"a": "x"}, "1": {"a": "y"}}),
            ({}, {}),
            ([], {}),
            # Scalar leaf values pass through unchanged
            ("hello", "hello"),
            (42, 42),
            (3.14, 3.14),
            (True, True),
            (None, None),
        ],
    )
    def test_flatten(self, data: object, expected: object) -> None:
        """Dicts are kept as-is; lists become dicts with string-index keys."""
        # Act
        result = flatten(data)

        # Assert
        assert result == expected


class TestUnflatten:
    """Tests for the unflatten function."""

    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            ({"a": "x"}, {"a": "x"}),
            ({"0": "x", "1": "y"}, ["x", "y"]),
            ({"0": {"a": "x"}, "1": {"a": "y"}}, [{"a": "x"}, {"a": "y"}]),
            # Mixed keys (numeric + non-numeric) stay as dict
            ({"a": "x", "0": "y"}, {"a": "x", "0": "y"}),
            ({"0": "a", "1": "b", "x": "c"}, {"0": "a", "1": "b", "x": "c"}),
            ({}, {}),
            # Unsorted digit keys → sorted into a list (Presidio may reorder keys)
            ({"1": "b", "0": "a"}, ["a", "b"]),
            # None value in a list-like dict
            ({"0": None, "1": "x"}, [None, "x"]),
            # Non-contiguous digit keys nested inside a dict value
            ({"a": {"0": "x", "2": "y"}}, {"a": {"0": "x", "2": "y"}}),
        ],
    )
    def test_unflatten(self, data: object, expected: object) -> None:
        """All-digit keys are converted back to lists; mixed keys stay as dicts."""
        # Act
        result = unflatten(data)

        # Assert
        assert result == expected


class TestRoundTrip:
    """Round-trip tests: unflatten(flatten(x)) must equal x."""

    @pytest.mark.parametrize(
        "data",
        [
            {"name": "Alice", "age": "30"},
            {"user": {"name": "Alice", "email": "alice@example.com"}},
            [{"name": "Alice"}, {"name": "Bob"}],
            {"tags": ["a", "b", "c"]},
            {"a": {"b": {"c": "deep"}}},
            [{"actor": {"name": "Alice", "mbox": "mailto:alice@example.com"}}],
            {"count": 42, "score": 3.14},
            {"active": True, "data": None},
            [None, "x", None],
            # Deeply nested lists
            [[["a"]]],
            # List of lists
            [["a", "b"], ["c", "d"]],
            # Empty dict inside a list
            [{}],
            # Mixed types in list
            [1, "a", True, None],
            {
                "statements": [
                    {
                        "actor": {
                            "name": "Alice",
                            "account": {
                                "homePage": "https://example.com",
                                "name": "alice",
                            },
                        },
                        "verb": {"id": "https://example.com/verbs/completed"},
                        "object": {
                            "id": "https://example.com/activities/1",
                            "definition": {
                                "name": {"en": "Activity 1"},
                                "extensions": [
                                    {"key": "score", "value": 42},
                                    {"key": "passed", "value": True},
                                ],
                            },
                        },
                    },
                    {
                        "actor": {
                            "name": "Bob",
                            "account": {
                                "homePage": "https://example.com",
                                "name": "bob",
                            },
                        },
                        "verb": {"id": "https://example.com/verbs/attempted"},
                        "object": {
                            "id": "https://example.com/activities/2",
                            "definition": {
                                "name": {"en": "Activity 2"},
                                "extensions": [{"key": "attempts", "value": 3}],
                            },
                        },
                    },
                ],
            },
        ],
    )
    def test_roundtrip(self, data: object) -> None:
        """Flattening then unflattening reconstructs the original structure."""
        # Act
        result = unflatten(flatten(data))

        # Assert
        assert result == data
