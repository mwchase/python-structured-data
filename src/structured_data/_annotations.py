import sys
import typing

from . import _ctor
from . import _nillable_write

_T = typing.TypeVar("_T")


def _all_annotations(
    cls: typing.Type[_T]
) -> typing.Iterator[typing.Tuple[typing.Type[_T], str, typing.Any]]:
    for superclass in reversed(cls.__mro__):
        for key, value in vars(superclass).get("__annotations__", {}).items():
            yield (superclass, key, value)


def _sum_args_from_annotations(cls: typing.Type[_T]) -> typing.Dict[str, typing.Tuple]:
    args: typing.Dict[str, typing.Tuple] = {}
    for superclass, key, value in _all_annotations(cls):
        _nillable_write.nillable_write(
            args, key, _ctor.get_args(value, vars(sys.modules[superclass.__module__]))
        )
    return args


def _product_args_from_annotations(
    cls: typing.Type[_T]
) -> typing.Dict[str, typing.Any]:
    args: typing.Dict[str, typing.Any] = {}
    for superclass, key, value in _all_annotations(cls):
        if value == "None" or _ctor.annotation_is_classvar(
            value, vars(sys.modules[superclass.__module__])
        ):
            value = None
        _nillable_write.nillable_write(args, key, value)
    return args
