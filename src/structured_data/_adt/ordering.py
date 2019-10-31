"""Helpers for reasoning about ordering methods."""

import typing


def ordering_options_are_valid(
    *, eq: bool, order: bool  # pylint: disable=invalid-name
) -> None:
    """Check constraint: we can't define order if we didn't define equality."""
    if order and not eq:
        raise ValueError("eq must be true if order is true")


def can_set_ordering(*, can_set: bool) -> bool:
    """Reduce cyclomatic complexity of the ``__init_subclass__`` methods."""
    if not can_set:
        raise ValueError("Can't add ordering methods if equality methods are provided.")
    return True


def raise_for_collision(collision: typing.Union[bool, None, str], name: str) -> None:
    """Create an informational message about ordering method collisions."""
    if collision:
        raise TypeError(
            f"Cannot overwrite attribute {collision} in class "
            f"{name}. Consider using functools.total_ordering"
        )
