import functools
import inspect
import typing

from ... import _class_placeholder
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


class Function(common.Decorator):
    """Decorator with value-based dispatch. Acts as a function."""

    def __init__(self, func: typing.Callable, *args, **kwargs) -> None:
        del func
        super().__init__(*args, **kwargs)  # type: ignore
        self.matchers = common.MatchTemplate()

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

    def __call__(self, /, *args, **kwargs):  # noqa: E225
        # Okay, so, this is a convoluted mess.

        bound_args, bound_kwargs, values = self._bound_and_values(args, kwargs)

        matchable_ = matchable.Matchable(values)
        for func in self.matchers.match(matchable_, None):
            return _dispatch(func, matchable_.matches, bound_args, bound_kwargs)
        # Hey, we can just fall back now.
        return self.__wrapped__(*args, **kwargs)

    def when(self, /, **kwargs) -> typing.Callable[[typing.Callable], typing.Callable]:  # noqa: E225
        """Add a binding for this function."""
        return common.decorate(self.matchers, _placeholder_kwargs(kwargs))


class MethodProxy:

    def __init__(self, func):
        self.func = func

    def __call__(self, /, *args, **kwargs):  # noqa: E225
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner):
        return self.func.__get__(instance, owner)


class Method(Function, common.Descriptor):
    """Decorator with value-based dispatch. Acts as a method."""

    def __get__(self, instance, owner):
        if instance is None:
            if owner is self.owner:
                return self
            return MethodProxy(self)
        return functools.partial(self, instance)

    def __call__(self, instance, /, *args, **kwargs):  # noqa: E225
        # Okay, so, this is a convoluted mess.

        bound_args, bound_kwargs, values = self._bound_and_values((instance,) + args, kwargs)

        matchable_ = matchable.Matchable(values)
        for func in self.matchers.match(matchable_, instance):
            return _dispatch(func, matchable_.matches, bound_args, bound_kwargs)
        # Hey, we can just fall back now.
        return self.__wrapped__(instance, *args, **kwargs)


def _kwarg_structure(kwargs: dict) -> mapping_match.DictPattern:
    return mapping_match.DictPattern(kwargs, exhaustive=True)


def _placeholder_kwargs(kwargs: typing.Dict) -> common.Matcher:
    if any(_class_placeholder.is_placeholder(kwarg) for kwarg in kwargs.values()):

        @_class_placeholder.placeholder
        def _placeholder(cls: type) -> mapping_match.DictPattern:
            return _kwarg_structure(
                {
                    name: (
                        kwarg(cls)
                        if _class_placeholder.is_placeholder(kwarg)
                        else kwarg
                    )
                    for (name, kwarg) in kwargs.items()
                }
            )

        return _placeholder

    return _kwarg_structure(kwargs)
