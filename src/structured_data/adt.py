"""Base classes for defining abstract data types.

This module provides three public members, which are used together.

Given a structure, possibly a choice of different structures, that you'd like
to associate with a type:

- First, create a class, that subclasses the Sum class.
- Then, for each possible structure, add an attribute annotation to the class
  with the desired name of the constructor, and a type of ``Ctor``, with the
  types within the constructor as arguments.

To look inside an ADT instance, use the functions from the
:mod:`structured_data.match` module.

Putting it together:

>>> from structured_data import match
>>> class Example(Sum):
...     FirstConstructor: Ctor[int, str]
...     SecondConstructor: Ctor[bytes]
...     ThirdConstructor: Ctor
...     def __iter__(self):
...         matchable = match.Matchable(self)
...         if matchable(Example.FirstConstructor(match.pat.count, match.pat.string)):
...             count, string = matchable[match.pat.count, match.pat.string]
...             for _ in range(count):
...                 yield string
...         elif matchable(Example.SecondConstructor(match.pat.bytes)):
...             bytes_ = matchable[match.pat.bytes]
...             for byte in bytes_:
...                 yield chr(byte)
...         elif matchable(Example.ThirdConstructor()):
...             yield "Third"
...             yield "Constructor"
>>> list(Example.FirstConstructor(5, "abc"))
['abc', 'abc', 'abc', 'abc', 'abc']
>>> list(Example.SecondConstructor(b"abc"))
['a', 'b', 'c']
>>> list(Example.ThirdConstructor())
['Third', 'Constructor']
"""

import inspect
import sys
import typing

from ._adt_constructor import ADTConstructor
from ._adt_constructor import make_constructor
from ._ctor import get_args
from ._prewritten_methods import SUBCLASS_ORDER
from ._prewritten_methods import PrewrittenProductMethods
from ._prewritten_methods import PrewrittenSumMethods

_T = typing.TypeVar("_T")


if typing.TYPE_CHECKING:  # pragma: nocover

    class Ctor:
        """Dummy class for type-checking purposes."""

    class ConcreteCtor(typing.Generic[_T]):
        """Wrapper class for type-checking purposes.

        The type parameter should be a Tuple type of fixed size.
        Classes containing this annotation (meaning they haven't been
        processed by the ``adt`` decorator) should not be instantiated.
        """


else:
    from ._ctor import Ctor


def _name(cls: typing.Type[_T], function) -> str:
    """Return the name of a function accessed through a descriptor."""
    return function.__get__(None, cls).__name__


def _set_new_functions(cls: typing.Type[_T], *functions) -> typing.Optional[str]:
    """Attempt to set the attributes corresponding to the functions on cls.

    If any attributes are already defined, fail *before* setting any, and
    return the already-defined name.
    """
    for function in functions:
        name = _name(cls, function)
        if getattr(object, name, None) is not getattr(cls, name, None):
            return name
    for function in functions:
        setattr(cls, _name(cls, function), function)
    return None


_K = typing.TypeVar("_K")
_V = typing.TypeVar("_V")


def _nillable_write(dct: typing.Dict[_K, _V], key: _K, value: typing.Optional[_V]):
    if value is None:
        dct.pop(key, typing.cast(_V, None))
    else:
        dct[key] = value


def _add_methods(cls: typing.Type[_T], do_set, *methods):
    methods_were_set = False
    if do_set:
        methods_were_set = not _set_new_functions(cls, *methods)
    return methods_were_set


def _set_hash(cls: typing.Type[_T], set_hash, src):
    if set_hash:
        cls.__hash__ = src.__hash__  # type: ignore


def _add_order(cls: typing.Type[_T], set_order, equality_methods_were_set, src):
    if set_order:
        if not equality_methods_were_set:
            raise ValueError(
                "Can't add ordering methods if equality methods are provided."
            )
        collision = _set_new_functions(
            cls, src.__lt__, src.__le__, src.__gt__, src.__ge__
        )
        if collision:
            raise TypeError(
                "Cannot overwrite attribute {collision} in class "
                "{name}. Consider using functools.total_ordering".format(
                    collision=collision, name=cls.__name__
                )
            )


def _sum_new(_cls: typing.Type[_T], subclasses):
    def base(cls, args):
        return super(_cls, cls).__new__(cls, args)

    new = _cls.__dict__.get("__new__", staticmethod(base))

    def __new__(cls, args):
        if cls not in subclasses:
            raise TypeError
        return new.__get__(None, cls)(cls, args)

    _cls.__new__ = staticmethod(__new__)  # type: ignore


def _product_new(
    _cls: typing.Type[_T],
    annotations: typing.Dict[str, typing.Any],
    defaults: typing.Dict[str, typing.Any],
):
    def __new__(*args, **kwargs):
        cls, *args = args
        return super(_cls, cls).__new__(cls, *args, **kwargs)

    __new__.__signature__ = inspect.signature(__new__).replace(
        parameters=[inspect.Parameter("cls", inspect.Parameter.POSITIONAL_ONLY)]
        + [
            inspect.Parameter(
                field,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=annotation,
                default=defaults.get(field, inspect.Parameter.empty),
            )
            for (field, annotation) in annotations.items()
        ]
    )
    _cls.__new__ = __new__


def _all_annotations(
    cls: typing.Type[_T]
) -> typing.Iterator[typing.Tuple[typing.Type[_T], str, typing.Any]]:
    for superclass in reversed(cls.__mro__):
        for key, value in vars(superclass).get("__annotations__", {}).items():
            yield (superclass, key, value)


def _sum_args_from_annotations(cls: typing.Type[_T]) -> typing.Dict[str, typing.Tuple]:
    args: typing.Dict[str, typing.Tuple] = {}
    for superclass, key, value in _all_annotations(cls):
        _nillable_write(
            args, key, get_args(value, vars(sys.modules[superclass.__module__]))
        )
    return args


def _product_args_from_annotations(
    cls: typing.Type[_T]
) -> typing.Dict[str, typing.Any]:
    args: typing.Dict[str, typing.Any] = {}
    for superclass, key, value in _all_annotations(cls):
        if value == "None":
            value = None
        _nillable_write(args, key, value)
    return args


def _tuple_getter(index: int):
    # TODO: __name__ and __qualname__
    @property
    def getter(self):
        return tuple.__getitem__(self, index)

    return getter


def _add_prewritten_methods(_cls: typing.Type[_T], _repr, eq, order, src):
    _set_new_functions(_cls, src.__setattr__, src.__delattr__)
    _set_new_functions(_cls, src.__bool__)

    _add_methods(_cls, _repr, src.__repr__)

    equality_methods_were_set = _add_methods(_cls, eq, src.__eq__, src.__ne__)

    _set_hash(_cls, equality_methods_were_set, src)

    _add_order(_cls, order, equality_methods_were_set, src)


def _process_class(_cls: typing.Type[_T], _repr, eq, order) -> typing.Type[_T]:
    if order and not eq:
        raise ValueError("eq must be true if order is true")

    subclass_order: typing.List[typing.Type[_T]] = []

    for name, args in _sum_args_from_annotations(_cls).items():
        make_constructor(_cls, name, args, subclass_order)

    SUBCLASS_ORDER[_cls] = tuple(subclass_order)

    _cls.__init_subclass__ = PrewrittenSumMethods.__init_subclass__  # type: ignore

    _sum_new(_cls, frozenset(subclass_order))

    _add_prewritten_methods(_cls, _repr, eq, order, PrewrittenSumMethods)

    return _cls


class Sum:
    """Base class of classes with disjoint constructors.

    Examines PEP 526 __annotations__ to determine subclasses.

    If repr is true, a __repr__() method is added to the class.
    If order is true, rich comparison dunder methods are added.

    The Sum class examines the class to find Ctor annotations.
    A Ctor annotation is the adt.Ctor class itself, or the result of indexing
    the class, either with a single type hint, or a tuple of type hints.
    All other annotations are ignored.

    The subclass is not subclassable, but has subclasses at each of the
    names that had Ctor annotations. Each subclass takes a fixed number of
    arguments, corresponding to the type hints given to its annotation, if any.
    """

    __slots__ = ()

    def __init_subclass__(cls, *, repr=True, eq=True, order=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if not issubclass(cls, ADTConstructor):
            _process_class(cls, repr, eq, order)


class Product(ADTConstructor, tuple):
    """Base class of classes with typed fields.

    Examines PEP 526 __annotations__ to determine fields.

    If repr is true, a __repr__() method is added to the class.
    If order is true, rich comparison dunder methods are added.

    The Product class examines the class to find annotations.
    Annotations with a value of "None" are discarded.
    Fields may have default values, and can be set to inspect.empty to
    indicate "no default".

    The subclass is subclassable. The implementation was designed with a focus
    on flexibility over ideals of purity, and therefore provides various
    optional facilities that conflict with, for example, Liskov
    substitutability. For the purposes of matching, each class is considered
    distinct.
    """

    __slots__ = ()

    def __new__(*args, **kwargs):
        cls, *args = args
        values = cls.__defaults.copy()
        fields_iter = iter(cls.__annotations)
        for arg, field in zip(args, fields_iter):
            values[field] = arg
        for field in fields_iter:
            if field in values and field not in kwargs:
                continue
            values[field] = kwargs.pop(field)
        if kwargs:
            raise TypeError(kwargs)
        return super(Product, cls).__new__(
            cls, [values[field] for field in cls.__annotations]
        )

    def __init_subclass__(cls, *, repr=True, eq=True, order=False, **kwargs):
        super().__init_subclass__(**kwargs)
        if "__annotations__" not in vars(cls):
            return
        if order and not eq:
            raise ValueError("eq must be true if order is true")

        cls.__annotations = _product_args_from_annotations(cls)

        cls.__defaults = {}
        field_names = iter(reversed(tuple(cls.__annotations)))
        for field in field_names:
            default = getattr(cls, field, inspect.Parameter.empty)
            if default is inspect.Parameter.empty:
                break
            cls.__defaults[field] = default
        for field in field_names:
            if (
                getattr(cls, field, inspect.Parameter.empty)
                is not inspect.Parameter.empty
            ):
                raise TypeError

        _product_new(cls, cls.__annotations, cls.__defaults)

        for index, field in enumerate(cls.__annotations):
            setattr(cls, field, _tuple_getter(index))

        _add_prewritten_methods(cls, repr, eq, order, PrewrittenProductMethods)


__all__ = ["Ctor", "Product", "Sum"]
