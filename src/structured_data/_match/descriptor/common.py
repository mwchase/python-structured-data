import functools
import typing

from ... import _class_placeholder
from .. import destructure


def _check_structure(structure):
    destructure.names(structure)  # Raise ValueError if there are duplicates


def decorate(matchers, structure):
    if not _class_placeholder.is_placeholder(structure):
        _check_structure(structure)

    def decorator(func):
        matchers.append((structure, func))
        return func

    return decorator


class Descriptor:
    """Base class for decorator classes."""

    __wrapped__ = None

    def __new__(cls, func, *args, **kwargs):
        new = super().__new__(cls, *args, **kwargs)
        new.__doc__ = None
        if func is None:
            return new
        return functools.wraps(func)(new)

    def _matchers(self) -> typing.Iterator[typing.List[typing.Tuple[typing.Any, typing.Callable]]]:
        raise NotImplementedError

    def for_class(self, cls: type) -> None:
        for matchers in self._matchers():
            for index, (structure_, func) in enumerate(matchers[:]):
                if _class_placeholder.is_placeholder(structure_):
                    structure = structure_(cls)
                    matchers[index] = (structure, func)


def for_class(cls: type) -> None:
    for attr in vars(cls).values():
        if isinstance(attr, Descriptor):
            attr.for_class(cls)
