"""An internal function for dealing with ADT instances."""

from __future__ import annotations

import typing

from . import _structure


def unpack(instance: tuple) -> tuple:
    """Return the inside of any ADT instance.

    This function is not meant for general use.
    """
    return tuple.__getitem__(instance, slice(None))


def structuring_unpack(
    instance: tuple,
) -> typing.Tuple[_structure.Structure[typing.Any]]:
    return unpack(instance)  # type: ignore


__all__ = ["unpack"]
