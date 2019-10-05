"""Helpers for reasoning about ordering methods."""


def _ordering_options_are_valid(
    *, eq: bool, order: bool  # pylint: disable=invalid-name
):
    if order and not eq:
        raise ValueError("eq must be true if order is true")


def _can_set_ordering(*, can_set: bool):
    if not can_set:
        raise ValueError("Can't add ordering methods if equality methods are provided.")
    return True
