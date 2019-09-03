"""Base class for Sum subclasses and Product.

Blocks access to many built-in methods.
"""

import inspect
import typing
import weakref

from . import _annotations

_T = typing.TypeVar("_T")


def _should_include(name, static):
    if name in SHADOWED_ATTRIBUTES and static is None:
        return False
    if isinstance(static, SumMember):
        return False
    return True


class ADTConstructor:
    """Base class for ADT Constructor classes."""

    __slots__ = ()

    def __dir__(self):
        return [
            attribute
            for attribute in super().__dir__()
            if _should_include(attribute, inspect.getattr_static(self, attribute))
        ]

    __eq__ = object.__eq__
    __ne__ = object.__ne__
    __hash__ = object.__hash__


SHADOWED_ATTRIBUTES = {
    "__add__",
    "__contains__",
    "__getitem__",
    "__iter__",
    "__len__",
    "__mul__",
    "__rmul__",
    "count",
    "index",
    "__lt__",
    "__le__",
    "__gt__",
    "__ge__",
}


for _attribute in SHADOWED_ATTRIBUTES:
    setattr(ADTConstructor, _attribute, None)


class SumMember:
    """Accessor for Sum subclass constructor, only accessible from the base."""
    def __init__(self, subcls: type):
        self.subcls = subcls

    def __get__(self, obj, cls):
        if cls is ADT_BASES[self.subcls] and obj is None:
            return self.subcls
        raise AttributeError("Can only access adt members through base class.")


ADT_BASES: typing.MutableMapping[type, type] = weakref.WeakKeyDictionary()


def make_constructor(_cls, name: str, args: typing.Tuple, subclass_order):
    """Create a subclass of _cls with a constructor generated from args."""
    length = len(args)

    # pylint: disable=missing-docstring
    class Constructor(_cls, ADTConstructor, tuple):  # type: ignore
        __doc__ = f"""Auto-generated subclass {name} of ADT {_cls.__qualname__}.

        Takes {length} argument{'' if length == 1 else 's'}.
        """

        __slots__ = ()

        def __new__(cls, *args):
            if len(args) != length:
                raise ValueError
            return super().__new__(cls, args)

    ADT_BASES[Constructor] = _cls

    Constructor.__name__ = name
    Constructor.__qualname__ = "{qualname}.{name}".format(
        qualname=_cls.__qualname__, name=name
    )

    setattr(_cls, name, SumMember(Constructor))
    subclass_order.append(Constructor)

    annotations = {f"_{index}": arg for (index, arg) in enumerate(args)}
    parameters = [
        inspect.Parameter(name, inspect.Parameter.POSITIONAL_ONLY, annotation=arg)
        for (name, arg) in annotations.items()
    ]
    annotations["return"] = _cls.__qualname__

    Constructor.__new__.__signature__ = inspect.Signature(  # type: ignore
        [inspect.Parameter("cls", inspect.Parameter.POSITIONAL_ONLY)] + parameters,
        return_annotation=_cls.__qualname__,
    )
    Constructor.__new__.__annotations__ = annotations


def make_constructors(cls: typing.Type[_T]):
    """Return all of the constructors of the given class in definition order."""
    subclass_order: typing.List[typing.Type[_T]] = []

    for name, args in _annotations.sum_args_from_annotations(cls).items():
        make_constructor(cls, name, args, subclass_order)

    return tuple(subclass_order)


__all__ = ["ADTConstructor", "make_constructor"]
