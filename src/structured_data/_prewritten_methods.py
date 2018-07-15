import inspect
import weakref

from ._enum_constructor import ENUM_BASES
from ._unpack import unpack


def enum_base(obj):
    return ENUM_BASES.get(obj.__class__)


MISSING = object()


SUBCLASS_ORDER = weakref.WeakKeyDictionary()


def cant_modify(self, name):
    class_repr = repr(self.__class__.__name__)
    name_repr = repr(name)
    if inspect.getattr_static(self, name, MISSING) is MISSING:
        format_msg = '{class_repr} object has no attribute {name_repr}'
    else:
        format_msg = '{class_repr} object attribute {name_repr} is read-only'
    raise AttributeError(
        format_msg.format(class_repr=class_repr, name_repr=name_repr))


class PrewrittenMethods:

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__qualname__,
            ", ".join(repr(item) for item in unpack(self)))

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) == unpack(other)
        if enum_base(other) is enum_base(self):
            return False
        return NotImplemented

    def __ne__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) != unpack(other)
        if enum_base(other) is enum_base(self):
            return True
        return NotImplemented

    def __lt__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) < unpack(other)
        if enum_base(other) is enum_base(self):
            order = SUBCLASS_ORDER.get(enum_base(self))
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index < other_index
        return NotImplemented

    def __le__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) <= unpack(other)
        if enum_base(other) is enum_base(self):
            order = SUBCLASS_ORDER.get(enum_base(self))
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index <= other_index
        return NotImplemented

    def __gt__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) > unpack(other)
        if enum_base(other) is enum_base(self):
            order = SUBCLASS_ORDER.get(enum_base(self))
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index > other_index
        return NotImplemented

    def __ge__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) >= unpack(other)
        if enum_base(other) is enum_base(self):
            order = SUBCLASS_ORDER.get(enum_base(self))
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index >= other_index
        return NotImplemented

    def __hash__(self):
        return hash(unpack(self))

    def __setattr__(self, name, value):
        cant_modify(self, name)

    def __delattr__(self, name):
        cant_modify(self, name)

    def __bool__(self):
        return True


__all__ = ['PrewrittenMethods']
