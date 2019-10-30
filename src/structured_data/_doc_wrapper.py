"""Wrapper to control documentation visibility."""


class DocWrapper:
    """Custom descriptor that hides class doc on instances."""
    def __init__(self, doc=None):
        self.doc = doc

    @classmethod
    def wrap_class(cls, klass):
        """Wrap a class's docstring to conceal it from instances."""
        klass.__doc__ = cls(klass.__doc__)
        return klass

    def __get__(self, instance, owner):
        if instance is None:
            return self.doc
        return vars(instance).get("__doc__")

    def __set__(self, instance, value):
        vars(instance)["__doc__"] = value

    def __delete__(self, instance):
        vars(instance).pop("__doc__", None)


class ProxyWrapper:
    """Custom descriptor that forwards instance doc to an attribute."""
    def __init__(self, name, doc):
        self.name = name
        self.doc = doc

    @classmethod
    def wrap_class(cls, name: str):
        """Wrap a proxy's docstring to forward it for instances."""
        def decorator(klass):
            klass.__doc__ = cls(name, klass.__doc__)
            return klass
        return decorator

    def __get__(self, instance, owner):
        if instance is None:
            return self.doc
        return getattr(instance, self.name).__doc__
