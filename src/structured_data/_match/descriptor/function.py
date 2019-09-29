import functools
import inspect

from ... import _pep_570_when
from .. import matchable
from ..patterns import mapping_match
from . import common


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


class Function(common.Descriptor):
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

        matchable_ = matchable.Matchable(values)
        for structure, func in self.matchers:
            if matchable_(structure):
                return _dispatch(func, matchable_.matches, bound_args, bound_kwargs)
        raise ValueError(values)

    @_pep_570_when.pep_570_when
    def when(self, kwargs):
        """Add a binding for this function."""
        return common.decorate(
            self.matchers, mapping_match.DictPattern(kwargs, exhaustive=True)
        )
