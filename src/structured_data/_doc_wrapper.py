class DocWrapper:
    def __init__(self, doc=None):
        self.doc = doc

    @classmethod
    def wrap_class(cls, klass):
        """Wrapp a classes docstring to conceal it from instances."""
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
