import functools
import inspect

from . import _destructure
from . import _doc_wrapper
from . import _matchable
from . import _pep_570_when
from ._patterns import mapping_match


def _decorate(matchers, structure, func):
    matchers.append((structure, func))
    return func


class Descriptor:
    """Base class for decorator classes."""

    __wrapped__ = None

    def __new__(cls, func, *args, **kwargs):
        new = super().__new__(cls, *args, **kwargs)
        new.__doc__ = None
        if func is None:
            return new
        return functools.wraps(func)(new)


@_doc_wrapper.DocWrapper.wrap_class
class Property(Descriptor):
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
        matchable = _matchable.Matchable(instance)
        for (structure, func) in self.get_matchers:
            if matchable(structure):
                return func(**matchable.matches)
        if self.__wrapped__ is None:
            raise ValueError(self)
        return self.__wrapped__(instance)

    def __set__(self, instance, value):
        matchable = _matchable.Matchable((instance, value))
        for (structure, func) in self.set_matchers:
            if matchable(structure):
                func(**matchable.matches)
                return
        if self.fset is None:
            raise ValueError((instance, value))
        self.fset(instance, value)

    def __delete__(self, instance):
        matchable = _matchable.Matchable(instance)
        for (structure, func) in self.delete_matchers:
            if matchable(structure):
                func(**matchable.matches)
                return
        if self.fdel is None:
            raise ValueError(instance)
        self.fdel(instance)

    def get_when(self, instance):
        """Add a binding to the getter."""
        structure = instance
        _destructure.names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.get_matchers, structure)

    def set_when(self, instance, value):
        """Add a binding to the setter."""
        structure = (instance, value)
        _destructure.names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.set_matchers, structure)

    def delete_when(self, instance):
        """Add a binding to the deleter."""
        structure = instance
        _destructure.names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.delete_matchers, structure)


def _varargs(signature):
    for parameter in signature.parameters.values():
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            yield parameter


def _dispatch(func, matches, bound_args, bound_kwargs):
    for key, value in matches.items():
        if key in bound_kwargs:
            raise TypeError
        bound_kwargs[key] = value
    function_sig = inspect.signature(func)
    function_args = function_sig.bind(**bound_kwargs)
    for parameter in _varargs(function_sig):
        function_args.arguments[parameter.name] = bound_args
    function_args.apply_defaults()
    return func(*function_args.args, **function_args.kwargs)


class Function(Descriptor):
    """Decorator with value-based dispatch. Acts as a function."""

    def __init__(self, func, *args, **kwargs):
        del func
        super().__init__(*args, **kwargs)
        self.matchers = []

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(self, instance)

    def _bound_and_values(self, args, kwargs):
        # Then we figure out what signature we're giving the outside world.
        signature = inspect.signature(self)
        # The signature lets us regularize the call and apply any defaults
        bound_arguments = signature.bind(*args, **kwargs)
        bound_arguments.apply_defaults()

        # Extract the *args and **kwargs, if any.
        # These are never used in the matching, just passed to the underlying function
        bound_args = ()
        bound_kwargs = {}
        values = bound_arguments.arguments.copy()
        for parameter in signature.parameters.values():
            if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
                bound_args = values.pop(parameter.name)
            if parameter.kind is inspect.Parameter.VAR_KEYWORD:
                bound_kwargs = values.pop(parameter.name)
        return bound_args, bound_kwargs, values

    def __call__(*args, **kwargs):
        # Okay, so, this is a convoluted mess.
        # First, we extract self from the beginning of the argument list
        self, *args = args

        bound_args, bound_kwargs, values = self._bound_and_values(args, kwargs)

        matchable = _matchable.Matchable(values)
        for structure, func in self.matchers:
            if matchable(structure):
                return _dispatch(func, matchable.matches, bound_args, bound_kwargs)
        raise ValueError(values)

    @_pep_570_when.pep_570_when
    def when(self, kwargs):
        """Add a binding for this function."""
        structure = mapping_match.DictPattern(kwargs, exhaustive=True)
        _destructure.names(structure)  # Raise ValueError if there are duplicates
        return functools.partial(_decorate, self.matchers, structure)
