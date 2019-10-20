import functools
import typing

from ... import _class_placeholder
from ..._adt import prewritten_methods
from .. import destructure

T = typing.TypeVar("T")

Matcher = typing.Union[T, typing.Callable[[type], T]]


def _apply(structure, base):
    if _class_placeholder.is_placeholder(structure):
        new = structure(base)
        _check_structure(new)
        return new
    _check_structure(structure)
    return structure


class MatchTemplate(typing.Generic[T]):
    def __init__(self) -> None:
        self._templates: typing.List[typing.Tuple[Matcher[T], typing.Callable]] = []
        self._abstract = False
        self._cache: typing.Dict[
            typing.Optional[type], typing.List[typing.Tuple[T, typing.Callable]]
        ] = {}

    def copy_into(self, other):
        for structure, func in self._templates:
            other.add_structure(structure, func)

    # @property
    # def abstract(self):
    #     return self._abstract

    def add_structure(self, structure, func):
        self._templates.append((structure, func))
        if _class_placeholder.is_placeholder(structure):
            self._abstract = True
            self._cache.pop(None, None)
        for base, structures in self._cache.items():
            structures.append((_apply(structure, base), func))

    def _get_matchers(self, base):
        if base in self._cache:
            return self._cache[base]
        return self._cache.setdefault(
            base,
            [(_apply(structure, base), func) for (structure, func) in self._templates],
        )

    def match(self, matchable, instance):
        base = prewritten_methods.sum_base(instance) if self._abstract else None
        if base is None and self._abstract:
            raise ValueError
        for structure, func in self._get_matchers(base):
            if matchable(structure):
                break
        else:
            return
        yield func


def _check_structure(structure) -> None:
    destructure.names(structure)  # Raise ValueError if there are duplicates


def decorate(matchers: MatchTemplate[T], structure: Matcher[T]):
    def decorator(func: typing.Callable) -> typing.Callable:
        matchers.add_structure(structure, func)
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
