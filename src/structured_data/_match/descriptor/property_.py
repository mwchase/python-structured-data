from ... import _doc_wrapper
from .. import matchable
from . import common


@_doc_wrapper.DocWrapper.wrap_class
class Property(common.Descriptor):
    """Decorator with value-based dispatch. Acts as a property."""

    fset = None
    fdel = None

    protected = False

    def __new__(cls, func=None, fset=None, fdel=None, doc=None, *args, **kwargs):
        del fset, fdel, doc
        return super().__new__(cls, func, *args, **kwargs)

    def __init__(self, func=None, fset=None, fdel=None, doc=None, *args, **kwargs):
        del func
        super().__init__(*args, **kwargs)
        self.fset = fset
        self.fdel = fdel
        if doc is not None:
            self.__doc__ = doc
        self.get_matchers = []
        self.set_matchers = []
        self.delete_matchers = []
        self.protected = True

    def __setattr__(self, name, value):
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if self.protected and name != "__doc__":
            raise AttributeError
        super().__delattr__(name)

    def getter(self, getter):
        """Return a copy of self with the getter replaced."""
        new = Property(getter, self.fset, self.fdel, self.__doc__)
        new.get_matchers.extend(self.get_matchers)
        new.set_matchers.extend(self.set_matchers)
        new.delete_matchers.extend(self.delete_matchers)
        return new

    def setter(self, setter):
        """Return a copy of self with the setter replaced."""
        new = Property(self.__wrapped__, setter, self.fdel, self.__doc__)
        new.get_matchers.extend(self.get_matchers)
        new.set_matchers.extend(self.set_matchers)
        new.delete_matchers.extend(self.delete_matchers)
        return new

    def deleter(self, deleter):
        """Return a copy of self with the deleter replaced."""
        new = Property(self.__wrapped__, self.fset, deleter, self.__doc__)
        new.get_matchers.extend(self.get_matchers)
        new.set_matchers.extend(self.set_matchers)
        new.delete_matchers.extend(self.delete_matchers)
        return new

    def __get__(self, instance, owner):
        if instance is None:
            return self
        matchable_ = matchable.Matchable(instance)
        for (structure, func) in self.get_matchers:
            if matchable_(structure):
                return func(**matchable_.matches)
        if self.__wrapped__ is None:
            raise ValueError(self)
        return self.__wrapped__(instance)

    def __set__(self, instance, value):
        matchable_ = matchable.Matchable((instance, value))
        for (structure, func) in self.set_matchers:
            if matchable_(structure):
                func(**matchable_.matches)
                return
        if self.fset is None:
            raise ValueError((instance, value))
        self.fset(instance, value)

    def __delete__(self, instance):
        matchable_ = matchable.Matchable(instance)
        for (structure, func) in self.delete_matchers:
            if matchable_(structure):
                func(**matchable_.matches)
                return
        if self.fdel is None:
            raise ValueError(instance)
        self.fdel(instance)

    def get_when(self, instance):
        """Add a binding to the getter."""
        return common.decorate(self.get_matchers, instance)

    def set_when(self, instance, value):
        """Add a binding to the setter."""
        return common.decorate(self.set_matchers, (instance, value))

    def delete_when(self, instance):
        """Add a binding to the deleter."""
        return common.decorate(self.delete_matchers, instance)
