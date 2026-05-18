from typing import Any


def flatten(node: Any) -> Any:  # noqa: ANN401
    """For Presidio: dicts pass through, lists become dicts with string-index keys."""
    if isinstance(node, dict):
        return {k: flatten(v) for k, v in node.items()}
    if isinstance(node, list):
        return {str(i): flatten(v) for i, v in enumerate(node)}
    return node


def unflatten(node: Any) -> Any:  # noqa: ANN401
    """Rebuild original JSON: list-like dicts are converted back to lists.

    Note: dicts whose keys are consecutive integers starting from 0
    (e.g. {"0": "a", "1": "b"}) are indistinguishable from flattened lists
    and will be returned as lists. This is a known limitation.
    """
    if isinstance(node, dict):
        if node:
            keys = node.keys()
            if all(k.isdigit() for k in keys):
                indices = sorted(int(k) for k in keys)
                if indices == list(range(len(indices))):
                    return [unflatten(node[str(i)]) for i in indices]
        return {k: unflatten(v) for k, v in node.items()}
    return node


def get_nested_value(data: dict[str, Any], path: tuple[str, ...]) -> Any:  # noqa: ANN401
    """Get a value from a nested dict using a tuple path.

    Tuple paths handle keys containing dots (e.g. email addresses as keys),
    unlike dot-separated string paths which would be ambiguous.
    """
    node: Any = data
    for key in path:
        node = node[key]
    return node


def set_nested_value(data: dict[str, Any], path: tuple[str, ...], value: Any) -> None:  # noqa: ANN401
    """Set a value in a nested dict using a tuple path.

    Tuple paths handle keys containing dots (e.g. email addresses as keys)
    unlike dot-separated string paths which would be ambiguous.
    All intermediate nodes along the path must already exist.
    """
    if not path:
        raise ValueError("Path cannot be empty")
    node: Any = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
