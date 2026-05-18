import pytest

from data_deidentifier.adapters.presidio.json_utils import (
    flatten,
    get_nested_value,
    set_nested_value,
    unflatten,
)


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


class TestGetNestedValue:
    """Tests for the get_nested_value function."""

    @pytest.mark.parametrize(
        ("data", "path", "expected"),
        [
            ({"a": "x"}, ("a",), "x"),
            ({"a": {"b": {"c": "x"}}}, ("a", "b", "c"), "x"),
            ({"users": {"0": {"name": "Alice"}}}, ("users", "0", "name"), "Alice"),
            # Key containing a dot
            ({"jacky@tuning.com": "x"}, ("jacky@tuning.com",), "x"),
            # Empty path returns the dict itself
            ({"a": "x"}, (), {"a": "x"}),
        ],
    )
    def test_get_nested_value(
        self,
        data: dict,
        path: tuple[str, ...],
        expected: object,
    ) -> None:
        """Navigates nested dict using a tuple path."""
        # Act
        result = get_nested_value(data, path)

        # Assert
        assert result == expected

    def test_missing_key_raises(self) -> None:
        """Raises KeyError for a missing key."""
        # Arrange
        data = {"a": "x"}

        # Act / Assert
        with pytest.raises(KeyError):
            get_nested_value(data, ("b",))


class TestSetNestedValue:
    """Tests for the set_nested_value function."""

    @pytest.mark.parametrize(
        ("data", "path", "value", "expected"),
        [
            ({"a": "x"}, ("a",), "y", {"a": "y"}),
            ({"a": {"b": {"c": "x"}}}, ("a", "b", "c"), "y", {"a": {"b": {"c": "y"}}}),
            (
                {"users": {"0": {"name": "Alice"}}},
                ("users", "0", "name"),
                "Bob",
                {"users": {"0": {"name": "Bob"}}},
            ),
            # Key containing a dot
            (
                {"jacky@tuning.com": "x"},
                ("jacky@tuning.com",),
                "y",
                {"jacky@tuning.com": "y"},
            ),
        ],
    )
    def test_set_nested_value(
        self,
        data: dict,
        path: tuple[str, ...],
        value: object,
        expected: dict,
    ) -> None:
        """Sets a value in a nested dict using a tuple path."""
        # Act
        set_nested_value(data, path, value)

        # Assert
        assert data == expected

    def test_adds_new_leaf_key(self) -> None:
        """Adds a new leaf key when intermediate nodes exist but the key does not."""
        # Arrange
        data = {"a": {}}

        # Act
        set_nested_value(data, ("a", "b"), "y")

        # Assert
        assert data == {"a": {"b": "y"}}

    def test_mutates_in_place(self) -> None:
        """Modifies the original dict, does not return a copy."""
        # Arrange
        data = {"a": {"b": "x"}}
        original_inner = data["a"]

        # Act
        set_nested_value(data, ("a", "b"), "y")

        # Assert
        assert data["a"] is original_inner
        assert data["a"]["b"] == "y"

    def test_empty_path_raises(self) -> None:
        """Raises ValueError for an empty path."""
        # Arrange
        data = {"a": "x"}

        # Act / Assert
        with pytest.raises(ValueError, match="Path cannot be empty"):
            set_nested_value(data, (), "y")

    def test_missing_intermediate_key_raises(self) -> None:
        """Raises KeyError when an intermediate key does not exist."""
        # Arrange
        data = {"a": {}}

        # Act / Assert
        with pytest.raises(KeyError):
            set_nested_value(data, ("a", "b", "c"), "y")

    def test_intermediate_not_dict_raises(self) -> None:
        """Raises TypeError when an intermediate node is not a dict."""
        # Arrange
        data = {"a": "x"}

        # Act / Assert
        with pytest.raises(TypeError):
            set_nested_value(data, ("a", "b"), "y")
