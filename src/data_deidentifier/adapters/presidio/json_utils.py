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
