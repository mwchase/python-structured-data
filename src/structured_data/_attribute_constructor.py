import weakref

ATTRIBUTE_CONSTRUCTORS = weakref.WeakKeyDictionary()
ATTRIBUTE_CACHE = weakref.WeakKeyDictionary()


class AttributeConstructor:

    __slots__ = ("__weakref__",)

    def __init__(self, constructor):
        ATTRIBUTE_CONSTRUCTORS[self] = constructor
        ATTRIBUTE_CACHE[self] = {}

    def __getattribute__(self, name):
        return ATTRIBUTE_CACHE[self].setdefault(
            name, ATTRIBUTE_CONSTRUCTORS[self](name)
        )
