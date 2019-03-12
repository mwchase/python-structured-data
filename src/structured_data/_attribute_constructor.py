import sys
import typing
import weakref

T = typing.TypeVar("T")

ATTRIBUTE_CONSTRUCTORS: typing.MutableMapping = weakref.WeakKeyDictionary()
ATTRIBUTE_CACHE: typing.MutableMapping = weakref.WeakKeyDictionary()


class AttributeConstructor(typing.Generic[T]):

    __slots__ = ("__weakref__",)

    def __init__(self, constructor: typing.Type[T]):
        ATTRIBUTE_CONSTRUCTORS[self] = constructor
        ATTRIBUTE_CACHE[self] = {}

    def __getattribute__(self, name: str) -> T:
        name = sys.intern(name)
        return ATTRIBUTE_CACHE[self].setdefault(
            name, ATTRIBUTE_CONSTRUCTORS[self](name)
        )
