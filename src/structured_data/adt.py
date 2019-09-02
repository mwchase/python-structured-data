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

from . import _adt_constructor
from . import _ctor
from . import _prewritten_methods

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


# This is fine.
def _name(cls: typing.Type[_T], function) -> str:
    """Return the name of a function accessed through a descriptor."""
    return function.__get__(None, cls).__name__


# This is mostly fine, though the list of classes is somewhat ad-hoc, to say
# the least.
def _cant_set_new_functions(cls: typing.Type[_T], *functions) -> typing.Optional[str]:
    for function in functions:
        name = _name(cls, function)
        existing = getattr(cls, name, None)
        if existing not in (
            getattr(object, name, None),
            getattr(Product, name, None),
            None,
            function,
        ):
            return name
    return None


def _set_new_functions(cls: typing.Type[_T], *functions) -> typing.Optional[str]:
    """Attempt to set the attributes corresponding to the functions on cls.

    If any attributes are already defined, fail *before* setting any, and
    return the already-defined name.
    """
    cant_set = _cant_set_new_functions(cls, *functions)
    if cant_set:
        return cant_set
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
            args, key, _ctor.get_args(value, vars(sys.modules[superclass.__module__]))
        )
    return args


def _product_args_from_annotations(
    cls: typing.Type[_T]
) -> typing.Dict[str, typing.Any]:
    args: typing.Dict[str, typing.Any] = {}
    for _, key, value in _all_annotations(cls):
        if value == "None" or _ctor.annotation_is_classvar(
            value, vars(sys.modules[cls.__module__])
        ):
            value = None
        _nillable_write(args, key, value)
    return args


def _ordering_options_are_valid(*, eq, order):
    if order and not eq:
        raise ValueError("eq must be true if order is true")


def _set_ordering(*, can_set, setter, cls, source):
    if not can_set:
        raise ValueError("Can't add ordering methods if equality methods are provided.")
    collision = setter(cls, source.__lt__, source.__le__, source.__gt__, source.__ge__)
    if collision:
        raise TypeError(
            "Cannot overwrite attribute {collision} in class "
            "{name}. Consider using functools.total_ordering".format(
                collision=collision, name=cls.__name__
            )
        )


def _extract_defaults(*, cls, annotations):
    defaults = {}
    field_names = iter(reversed(tuple(annotations)))
    for field in field_names:
        default = getattr(cls, field, inspect.Parameter.empty)
        if default is inspect.Parameter.empty:
            break
        defaults[field] = default
    for field in field_names:
        if getattr(cls, field, inspect.Parameter.empty) is not inspect.Parameter.empty:
            raise TypeError
    return defaults


def _unpack_args(*, args, kwargs, fields, values):
    fields_iter = iter(fields)
    for arg, field in zip(args, fields_iter):
        values[field] = arg
    for field in fields_iter:
        if field in values and field not in kwargs:
            continue
        values[field] = kwargs.pop(field)
    if kwargs:
        raise TypeError(kwargs)


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

    def __new__(*args, **kwargs):  # pylint: disable=no-method-argument
        cls, *args = args
        if not issubclass(cls, _adt_constructor.ADTConstructor):
            raise TypeError
        return super(Sum, cls).__new__(cls, *args, **kwargs)

    # Both of these are for consistency with modules defined in the stdlib.
    # BOOM!
    def __init_subclass__(
        cls,
        *,
        repr=True,  # pylint: disable=redefined-builtin
        eq=True,  # pylint: disable=invalid-name
        order=False,
        **kwargs
    ):
        super().__init_subclass__(**kwargs)
        if issubclass(cls, _adt_constructor.ADTConstructor):
            return
        _ordering_options_are_valid(eq=eq, order=order)

        subclass_order: typing.List[typing.Type[_T]] = []

        for name, args in _sum_args_from_annotations(cls).items():
            _adt_constructor.make_constructor(cls, name, args, subclass_order)

        _prewritten_methods.SUBCLASS_ORDER[cls] = tuple(subclass_order)

        cls.__init_subclass__ = (
            _prewritten_methods.PrewrittenSumMethods.__init_subclass__
        )  # type: ignore

        _sum_new(cls, frozenset(subclass_order))

        _set_new_functions(
            cls,
            _prewritten_methods.PrewrittenSumMethods.__setattr__,
            _prewritten_methods.PrewrittenSumMethods.__delattr__,
        )
        _set_new_functions(cls, _prewritten_methods.PrewrittenSumMethods.__bool__)

        if repr:
            _set_new_functions(cls, _prewritten_methods.PrewrittenSumMethods.__repr__)

        equality_methods_were_set = False
        if eq:
            equality_methods_were_set = not _set_new_functions(
                cls,
                _prewritten_methods.PrewrittenSumMethods.__eq__,
                _prewritten_methods.PrewrittenSumMethods.__ne__,
            )

        if equality_methods_were_set:
            cls.__hash__ = _prewritten_methods.PrewrittenSumMethods.__hash__

        if order:
            _set_ordering(
                can_set=equality_methods_were_set,
                setter=_set_new_functions,
                cls=cls,
                source=_prewritten_methods.PrewrittenSumMethods,
            )


class Product(_adt_constructor.ADTConstructor, tuple):
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

    def __new__(*args, **kwargs):  # pylint: disable=no-method-argument
        cls, *args = args
        if cls is Product:
            raise TypeError
        # Probably a result of not having positional-only args.
        values = cls.__defaults.copy()  # pylint: disable=protected-access
        _unpack_args(
            args=args,
            kwargs=kwargs,
            fields=cls.__fields,  # pylint: disable=protected-access
            values=values,
        )
        return super(Product, cls).__new__(
            cls,
            [
                values[field]
                for field in cls.__fields  # pylint: disable=protected-access
            ],
        )

    __repr = True
    __eq = True
    __order = False
    __eq_succeeded = None

    # Both of these are for consistency with modules defined in the stdlib.
    # BOOM!
    def __init_subclass__(
        cls,
        *,
        repr=None,  # pylint: disable=redefined-builtin
        eq=None,  # pylint: disable=invalid-name
        order=None,
        **kwargs
    ):
        super().__init_subclass__(**kwargs)

        if repr is not None:
            cls.__repr = repr
        if eq is not None:
            cls.__eq = eq
        if order is not None:
            cls.__order = order

        _ordering_options_are_valid(eq=cls.__eq, order=cls.__order)

        cls.__annotations = _product_args_from_annotations(cls)
        cls.__fields = {field: index for (index, field) in enumerate(cls.__annotations)}

        cls.__defaults = _extract_defaults(cls=cls, annotations=cls.__annotations)

        _product_new(cls, cls.__annotations, cls.__defaults)

        cls.__eq_succeeded = False
        if cls.__eq:
            cls.__eq_succeeded = not _cant_set_new_functions(
                cls,
                _prewritten_methods.PrewrittenProductMethods.__eq__,
                _prewritten_methods.PrewrittenProductMethods.__ne__,
            )

        if cls.__order:
            _set_ordering(
                can_set=cls.__eq_succeeded,
                setter=_cant_set_new_functions,
                cls=cls,
                source=_prewritten_methods.PrewrittenProductMethods,
            )

    def __dir__(self):
        return super().__dir__() + list(self.__fields)

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            index = self.__fields.get(name)
            if index is None:
                raise
            return tuple.__getitem__(self, index)

    __setattr__ = _prewritten_methods.PrewrittenProductMethods.__setattr__
    __delattr__ = _prewritten_methods.PrewrittenProductMethods.__delattr__
    __bool__ = _prewritten_methods.PrewrittenProductMethods.__bool__

    @property
    def __repr__(self):
        if self.__repr:
            return _prewritten_methods.PrewrittenProductMethods.__repr__.__get__(
                self, type(self)
            )
        return super().__repr__

    @property
    def __hash__(self):
        if self.__eq_succeeded:
            return _prewritten_methods.PrewrittenProductMethods.__hash__.__get__(
                self, type(self)
            )
        return super().__hash__

    @property
    def __eq__(self):  # pylint: disable=unexpected-special-method-signature
        if self.__eq_succeeded:
            # I think this is a Pylint bug, but I'm not sure how to reduce it.
            # pylint: disable=no-value-for-parameter
            return _prewritten_methods.PrewrittenProductMethods.__eq__.__get__(
                self, type(self)
            )
        return super().__eq__

    @property
    def __ne__(self):  # pylint: disable=unexpected-special-method-signature
        if self.__eq_succeeded:
            # I think this is a Pylint bug, but I'm not sure how to reduce it.
            # pylint: disable=no-value-for-parameter
            return _prewritten_methods.PrewrittenProductMethods.__ne__.__get__(
                self, type(self)
            )
        return super().__ne__

    @property
    def __lt__(self):  # pylint: disable=unexpected-special-method-signature
        if self.__order:
            # I think this is a Pylint bug, but I'm not sure how to reduce it.
            # pylint: disable=no-value-for-parameter
            return _prewritten_methods.PrewrittenProductMethods.__lt__.__get__(
                self, type(self)
            )
        return super().__lt__

    @property
    def __le__(self):  # pylint: disable=unexpected-special-method-signature
        if self.__order:
            # I think this is a Pylint bug, but I'm not sure how to reduce it.
            # pylint: disable=no-value-for-parameter
            return _prewritten_methods.PrewrittenProductMethods.__le__.__get__(
                self, type(self)
            )
        return super().__le__

    @property
    def __gt__(self):  # pylint: disable=unexpected-special-method-signature
        if self.__order:
            # I think this is a Pylint bug, but I'm not sure how to reduce it.
            # pylint: disable=no-value-for-parameter
            return _prewritten_methods.PrewrittenProductMethods.__gt__.__get__(
                self, type(self)
            )
        return super().__gt__

    @property
    def __ge__(self):  # pylint: disable=unexpected-special-method-signature
        if self.__order:
            # I think this is a Pylint bug, but I'm not sure how to reduce it.
            # pylint: disable=no-value-for-parameter
            return _prewritten_methods.PrewrittenProductMethods.__ge__.__get__(
                self, type(self)
            )
        return super().__ge__


__all__ = ["Ctor", "Product", "Sum"]
