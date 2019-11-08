"""Internal implementation of the Product base class."""

import inspect
import typing

import typing_extensions

from .. import _cant_modify
from .. import _conditional_method
from . import annotations
from . import constructor
from . import ordering
from . import prewritten_methods

TProduct = typing.TypeVar("TProduct", bound="Product")


class Named(typing_extensions.Protocol):

    __name__: str


class MethodLike(typing_extensions.Protocol):
    def __get__(self, instance: typing.Any, owner: type) -> Named:
        """Methods allow for binding and have names."""


def name_(cls: type, function: MethodLike) -> str:
    """Return the name of a function accessed through a descriptor."""
    return function.__get__(None, cls).__name__


def cant_set_new_functions(
    cls: type, *functions: typing.Callable
) -> typing.Optional[str]:
    """Determine if attributes corresponding to functions on cls could be set.

    If any attributes are already defined, return the already-defined name.
    """
    for function in functions:
        name = name_(cls, typing.cast(MethodLike, function))
        existing = getattr(cls, name, None)
        if existing not in (
            getattr(object, name, None),
            getattr(Product, name, None),
            None,
            function,
        ):
            return name
    return None


def _product_new(_cls: typing.Type[TProduct], _signature: inspect.Signature) -> None:
    signature: inspect.Signature
    if "__new__" in vars(_cls):
        original_new = _cls.__new__

        def __new__(
            cls: typing.Type[TProduct],
            /,  # noqa: E225
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> TProduct:
            if cls is _cls:
                return original_new(cls, *args, **kwargs)
            return super(_cls, cls).__new__(cls, *args, **kwargs)

        signature = inspect.signature(original_new)
    else:

        def __new__(
            cls: typing.Type[TProduct],
            /,  # noqa: E225
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> TProduct:
            return super(_cls, cls).__new__(cls, *args, **kwargs)

        signature = _signature.replace(
            parameters=[inspect.Parameter("cls", inspect.Parameter.POSITIONAL_ONLY)]
            + list(_signature.parameters.values())
        )
    __new__.__signature__ = signature  # type: ignore
    _cls.__new__ = __new__  # type: ignore


def _product_signature(
    annotations_: typing.Dict[str, typing.Any], cls: typing.Type[TProduct]
) -> inspect.Signature:
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
        return inspect.Signature(parameters=params, return_annotation=cls)
    except ValueError:
        raise TypeError


class Product(constructor.ADTConstructor, tuple, constructor.ProductBase):
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

    def __new__(
        cls: typing.Type[TProduct],
        /,  # noqa: E225
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> TProduct:
        if cls is Product:
            raise TypeError
        # Probably a result of not having positional-only args.
        bound_arguments = cls.__signature.bind(
            *args, **kwargs
        )  # pylint: disable=protected-access
        bound_arguments.apply_defaults()
        return super().__new__(cls, bound_arguments.arguments.values())

    __repr: typing.ClassVar[bool] = True
    __eq: typing.ClassVar[bool] = True
    __order: typing.ClassVar[bool] = False
    __eq_succeeded = None

    __signature: typing.ClassVar[inspect.Signature]
    __fields: typing.ClassVar[typing.Dict[str, int]]

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
        **kwargs: typing.Any,
    ):
        super().__init_subclass__(**kwargs)  # type: ignore

        cls.__repr = repr  # type: ignore
        cls.__eq = eq  # type: ignore
        cls.__order = order  # type: ignore

        del repr, eq, order
        cls.__clear_nones()

        ordering.ordering_options_are_valid(eq=cls.__eq, order=cls.__order)

        annotations_ = annotations.product_args_from_annotations(cls)
        cls.__signature = _product_signature(annotations_, cls)
        cls.__fields = {field: index for (index, field) in enumerate(annotations_)}

        _product_new(cls, cls.__signature)

        source = prewritten_methods.PrewrittenProductMethods

        cls.__eq_succeeded = cls.__eq and not cant_set_new_functions(
            cls, source.__eq__, source.__ne__
        )

        ordering.raise_for_collision(
            (
                cls.__order
                and ordering.can_set_ordering(can_set=cls.__eq_succeeded)
                and cant_set_new_functions(
                    cls, source.__lt__, source.__le__, source.__gt__, source.__ge__
                )
            ),
            cls.__name__,
        )

    def __dir__(self) -> typing.List[str]:
        super_dir: typing.List[str]
        super_dir = super().__dir__()
        return super_dir + list(self.__fields)

    def __getattribute__(self, name: str) -> typing.Any:
        index = object.__getattribute__(self, "_Product__fields").get(name)
        if index is None:
            return super().__getattribute__(name)
        return tuple.__getitem__(self, index)

    def __setattr__(self, name: str, value: typing.Any) -> None:
        _cant_modify.guard(self, name)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        _cant_modify.guard(self, name)
        super().__delattr__(name)

    def __bool__(self) -> bool:
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
