import inspect

MISSING = object()


def cant_modify(self, name):
    """Prevent attempts to modify an attr of the given name."""
    class_repr = repr(self.__class__.__name__)
    name_repr = repr(name)
    if inspect.getattr_static(self, name, MISSING) is MISSING:
        format_msg = "{class_repr} object has no attribute {name_repr}"
    else:
        format_msg = "{class_repr} object attribute {name_repr} is read-only"
    raise AttributeError(format_msg.format(class_repr=class_repr, name_repr=name_repr))
