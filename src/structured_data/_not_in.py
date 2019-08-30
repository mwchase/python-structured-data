"""A utility function for guarding when adding elements to containers."""

import typing

Item = typing.TypeVar("Item")


def not_in(*, container: typing.Container[Item], item: Item):
    """Raise ValueError if ``item`` is in ``container``."""
    if item in container:
        raise ValueError
