import inspect
import typing

from .. import _cant_modify
from .. import _conditional_method
from . import annotations
from . import constructor
from . import ordering
from . import prewritten_methods

_T = typing.TypeVar("_T")


def _name(cls: type, function) -> str:
    """Return the name of a function accessed through a descriptor."""
    return function.__get__(None, cls).__name__


def _cant_set_new_functions(cls: type, *functions) -> typing.Optional[str]:
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


def _product_new(_cls: typing.Type[_T], _signature):
    if "__new__" in vars(_cls):
        original_new = _cls.__new__

        def __new__(*args, **kwargs):
            cls, *args = args
            if cls is _cls:
                return original_new(cls, *args, **kwargs)
            return super(_cls, cls).__new__(cls, *args, **kwargs)

        signature = inspect.signature(original_new)
    else:

        def __new__(*args, **kwargs):
            cls, *args = args
            return super(_cls, cls).__new__(cls, *args, **kwargs)

        signature = _signature.replace(
            parameters=[inspect.Parameter("cls", inspect.Parameter.POSITIONAL_ONLY)]
            + list(_signature.parameters.values())
        )
    __new__.__signature__ = signature  # type: ignore
    _cls.__new__ = __new__  # type: ignore


class Product(constructor.ADTConstructor, tuple):
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
        bound_arguments = cls.__signature.bind(
            *args, **kwargs
        )  # pylint: disable=protected-access
        bound_arguments.apply_defaults()
        return super(Product, cls).__new__(cls, bound_arguments.arguments.values())

    __repr: typing.ClassVar[bool] = True
    __eq: typing.ClassVar[bool] = True
    __order: typing.ClassVar[bool] = False
    __eq_succeeded = None

    @classmethod
    def __clear_nones(cls) -> None:
        if cls.__repr is None:
            del cls.__repr
        if cls.__eq is None:
            del cls.__eq
        if cls.__order is None:
            del cls.__order

    # Both of these are for consistency with modules defined in the stdlib.
    # BOOM!
    def __init_subclass__(
        cls,
        *,
        repr: typing.Optional[bool] = None,  # pylint: disable=redefined-builtin
        eq: typing.Optional[bool] = None,  # pylint: disable=invalid-name
        order: typing.Optional[bool] = None,
        **kwargs,
    ):
        super().__init_subclass__(**kwargs)  # type: ignore

        cls.__repr = repr  # type: ignore
        cls.__eq = eq  # type: ignore
        cls.__order = order  # type: ignore

        del repr, eq, order
        cls.__clear_nones()

        ordering._ordering_options_are_valid(eq=cls.__eq, order=cls.__order)

        annotations_ = annotations.product_args_from_annotations(cls)
        params = [
            inspect.Parameter(
                name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                default=getattr(cls, name, inspect.Parameter.empty),
                annotation=annotation,
            )
            for (name, annotation) in annotations_.items()
        ]
        try:
            cls.__signature = inspect.Signature(
                parameters=params, return_annotation=cls
            )
        except ValueError:
            raise TypeError
        cls.__fields = {field: index for (index, field) in enumerate(annotations_)}

        _product_new(cls, cls.__signature)

        source = prewritten_methods.PrewrittenProductMethods

        cls.__eq_succeeded = cls.__eq and not _cant_set_new_functions(
            cls, source.__eq__, source.__ne__
        )

        if cls.__order:
            ordering._can_set_ordering(can_set=cls.__eq_succeeded)
            ordering._set_ordering(
                setter=_cant_set_new_functions, cls=cls, source=source
            )

    def __dir__(self):
        return super().__dir__() + list(self.__fields)

    def __getattribute__(self, name):
        index = object.__getattribute__(self, "_Product__fields").get(name)
        if index is None:
            return super().__getattribute__(name)
        return tuple.__getitem__(self, index)

    def __setattr__(self, name, value):
        if not inspect.isdatadescriptor(
            inspect.getattr_static(self, name, _cant_modify.MISSING)
        ):
            _cant_modify.cant_modify(self, name)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if not inspect.isdatadescriptor(
            inspect.getattr_static(self, name, _cant_modify.MISSING)
        ):
            _cant_modify.cant_modify(self, name)
        super().__delattr__(name)

    def __bool__(self):
        return True

    source = prewritten_methods.PrewrittenProductMethods

    # pylint: disable=protected-access
    __repr__ = _conditional_method.conditional_method(source).__repr  # type: ignore
    __hash__ = _conditional_method.conditional_method(  # type: ignore
        source
    ).__eq_succeeded
    __eq__ = _conditional_method.conditional_method(  # type: ignore
        source
    ).__eq_succeeded
    __ne__ = _conditional_method.conditional_method(  # type: ignore
        source
    ).__eq_succeeded
    __lt__ = _conditional_method.conditional_method(source).__order  # type: ignore
    __le__ = _conditional_method.conditional_method(source).__order  # type: ignore
    __gt__ = _conditional_method.conditional_method(source).__order  # type: ignore
    __ge__ = _conditional_method.conditional_method(source).__order  # type: ignore

    del source
