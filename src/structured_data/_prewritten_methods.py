import inspect

from _unpack import unpack


def _enum_base(obj):
    return getattr(obj.__class__, '__enum_base__', None)


_MISSING = object()


def _cant_modify(self, name):
    class_repr = repr(self.__class__.__name__)
    name_repr = repr(name)
    if inspect.getattr_static(self, name, _MISSING) is _MISSING:
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
        if _enum_base(other) is _enum_base(self):
            return False
        return NotImplemented

    def __ne__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) != unpack(other)
        if _enum_base(other) is _enum_base(self):
            return True
        return NotImplemented

    def __lt__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) < unpack(other)
        if _enum_base(other) is _enum_base(self):
            order = _enum_base(self).__subclass_order__
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index < other_index
        return NotImplemented

    def __le__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) <= unpack(other)
        if _enum_base(other) is _enum_base(self):
            order = _enum_base(self).__subclass_order__
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index <= other_index
        return NotImplemented

    def __gt__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) > unpack(other)
        if _enum_base(other) is _enum_base(self):
            order = _enum_base(self).__subclass_order__
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index > other_index
        return NotImplemented

    def __ge__(self, other):
        if other.__class__ is self.__class__:
            return unpack(self) >= unpack(other)
        if _enum_base(other) is _enum_base(self):
            order = _enum_base(self).__subclass_order__
            self_index = order.index(self.__class__)
            other_index = order.index(other.__class__)
            return self_index >= other_index
        return NotImplemented

    def __hash__(self):
        return hash(unpack(self))

    def __setattr__(self, name, value):
        _cant_modify(self, name)

    def __delattr__(self, name):
        _cant_modify(self, name)

    def __bool__(self):
        return True
