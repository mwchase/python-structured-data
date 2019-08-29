"""A utility function for guarding when adding elements to containers."""

import typing

T = typing.TypeVar("T")  # pylint: disable=invalid-name


def not_in(container: typing.Container[T], name: T):
    """Raise ValueError if ``name`` is in ``container``."""
    if name in container:
        raise ValueError
