import inspect
import weakref


class ADTConstructor:
    """Base class for ADT Constructor classes."""

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        """Explicitly forward to base class."""
        return super().__new__(cls, *args, **kwargs)

    def __dir__(self):
        super_dir = super().__dir__()
        my_dir = []
        for attribute in super_dir:
            static_attribute = inspect.getattr_static(self, attribute)
            if attribute in SHADOWED_ATTRIBUTES and static_attribute is None:
                continue
            if isinstance(static_attribute, ADTMember):
                continue
            my_dir.append(attribute)
        return my_dir

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


class ADTMember:
    def __init__(self, subcls):
        self.subcls = subcls

    def __get__(self, obj, cls):
        if cls is ENUM_BASES[self.subcls] and obj is None:
            return self.subcls
        raise AttributeError("Can only access adt members through base class.")


ENUM_BASES = weakref.WeakKeyDictionary()


def make_constructor(_cls, name, args, subclasses, subclass_order):
    length = len(args)

    class Constructor(_cls, ADTConstructor, tuple):
        """Auto-generated subclass of an ADT."""

        __slots__ = ()

        def __new__(cls, *args):
            if len(args) != length:
                raise ValueError
            return super().__new__(cls, args)

    ENUM_BASES[Constructor] = _cls

    Constructor.__name__ = name
    Constructor.__qualname__ = "{qualname}.{name}".format(
        qualname=_cls.__qualname__, name=name
    )

    subclasses.add(Constructor)
    setattr(_cls, name, ADTMember(Constructor))
    subclass_order.append(Constructor)

    annotations = {f"_{index}": arg for (index, arg) in enumerate(args)}
    parameters = [
        inspect.Parameter(name, inspect.Parameter.POSITIONAL_ONLY, annotation=arg)
        for (name, arg) in annotations.items()
    ]
    annotations["return"] = _cls.__qualname__

    Constructor.__new__.__signature__ = inspect.Signature(
        parameters, return_annotation=_cls.__qualname__
    )
    Constructor.__new__.__annotations__ = annotations


__all__ = ["ADTConstructor", "make_constructor"]
