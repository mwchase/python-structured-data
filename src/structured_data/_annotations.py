"""Helper functions for processing annotations."""

import sys
import typing

from . import _ctor
from . import _nillable_write


def _all_annotations(cls: type) -> typing.Iterator[typing.Tuple[type, str, typing.Any]]:
    for superclass in reversed(cls.__mro__):
        for key, value in vars(superclass).get("__annotations__", {}).items():
            yield (superclass, key, value)


def sum_args_from_annotations(cls: type) -> typing.Dict[str, typing.Tuple]:
    """Return the constructor data for Sum classes."""
    args: typing.Dict[str, typing.Tuple] = {}
    for superclass, key, value in _all_annotations(cls):
        _nillable_write.nillable_write(
            args, key, _ctor.get_args(value, vars(sys.modules[superclass.__module__]))
        )
    return args


def product_args_from_annotations(cls: type) -> typing.Dict[str, typing.Any]:
    """Return the field data for Product classes."""
    args: typing.Dict[str, typing.Any] = {}
    for superclass, key, value in _all_annotations(cls):
        if value == "None" or _ctor.annotation_is_classvar(
            value, vars(sys.modules[superclass.__module__])
        ):
            value = None
        _nillable_write.nillable_write(args, key, value)
    return args
