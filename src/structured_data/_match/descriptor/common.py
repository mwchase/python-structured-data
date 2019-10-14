import functools
import typing

from ... import _class_placeholder
from .. import destructure

T = typing.TypeVar("T")

Matcher = typing.Union[T, typing.Callable[[type], T]]
MatcherList = typing.List[typing.Tuple[Matcher[T], typing.Callable]]


def _check_structure(structure) -> None:
    destructure.names(structure)  # Raise ValueError if there are duplicates


def decorate(matchers: MatcherList[T], structure: Matcher[T]):
    if not _class_placeholder.is_placeholder(structure):
        _check_structure(structure)

    def decorator(func: typing.Callable) -> typing.Callable:
        matchers.append((structure, func))
        return func

    return decorator


class Decorator:
    """Base class for decorator classes."""

    __wrapped__ = None

    def __new__(cls, func, *args, **kwargs):
        new = super().__new__(cls, *args, **kwargs)
        new.__doc__ = None
        if func is None:
            return new
        return functools.wraps(func)(new)


class Descriptor(Decorator):
    owner: type

    def __set_name__(self, owner, name):
        if getattr(self, "owner", owner) is not owner:
            return
        self.owner = owner

    def _matchers(
        self
    ) -> typing.Iterator[typing.List[typing.Tuple[typing.Any, typing.Callable]]]:
        raise NotImplementedError

    def for_class(self, cls: type) -> None:
        for matchers in self._matchers():
            matchers[:] = [
                (
                    (structure(cls), func)
                    if _class_placeholder.is_placeholder(structure)
                    else (structure, func)
                )
                for (structure, func) in matchers
            ]


def for_class(cls: type) -> None:
    for attr in vars(cls).values():
        if isinstance(attr, Descriptor):
            attr.for_class(cls)
