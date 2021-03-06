"""Callable descriptors that expose decorators for value-based dispatch."""

from __future__ import annotations

import functools
import inspect
import typing

from ... import _class_placeholder
from ... import _doc_wrapper
from .. import matchable
from ..patterns import mapping_match
from . import common

T = typing.TypeVar("T")

Kwargs = typing.Dict[str, typing.Any]


def _varargs(signature: inspect.Signature) -> typing.Iterator[inspect.Parameter]:
    for parameter in signature.parameters.values():
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            yield parameter


def _dispatch(
    func: typing.Callable,
    matches: typing.Mapping,
    bound_args: typing.Tuple,
    bound_kwargs: Kwargs,
) -> typing.Any:
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


def _bound_and_values(
    signature: inspect.Signature, args: typing.Tuple, kwargs: Kwargs,
) -> typing.Tuple[typing.Tuple, Kwargs, Kwargs]:
    # The signature lets us regularize the call and apply any defaults
    bound_arguments = signature.bind(*args, **kwargs)
    bound_arguments.apply_defaults()

    # Extract the *args and **kwargs, if any.
    # These are never used in the matching, just passed to the underlying function
    bound_args = ()
    bound_kwargs: Kwargs = {}
    values = bound_arguments.arguments.copy()
    for parameter in signature.parameters.values():
        if parameter.kind is inspect.Parameter.VAR_POSITIONAL:
            bound_args = values.pop(parameter.name)
        if parameter.kind is inspect.Parameter.VAR_KEYWORD:
            bound_kwargs = values.pop(parameter.name)
    return bound_args, bound_kwargs, values


class ClassMethod(common.Descriptor):
    """Decorator with value-based dispatch. Acts as a classmethod."""

    __wrapped__: typing.Callable

    def __init__(self, func: typing.Callable) -> None:
        del func
        super().__init__()
        # A more specific annotation would be good, but that's waiting on
        # further development.
        self.matchers: common.MatchTemplate[typing.Any] = common.MatchTemplate()

    def __get__(self, instance, owner):
        if instance is None and common.owns(self, owner):
            return ClassMethodWhen(self, owner)
        return ClassMethodCall(self, owner)

    def when(
        self, /, **kwargs: typing.Any  # noqa: E225
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Add a binding for this function."""
        return common.decorate(self.matchers, _placeholder_kwargs(kwargs))


@_doc_wrapper.ProxyWrapper.wrap_class("class_method")
class ClassMethodCall:
    """Wrapper class that conceals the ``when()`` decorators."""

    def __init__(self, class_method: ClassMethod, owner: type) -> None:
        self.class_method = class_method
        self.owner = owner

    def __call__(
        self, /, *args: typing.Any, **kwargs: typing.Any  # noqa: E225
    ) -> typing.Any:
        bound_args, bound_kwargs, values = _bound_and_values(
            inspect.signature(self.class_method.__wrapped__),
            (self.owner,) + args,
            kwargs,
        )

        matchable_ = matchable.Matchable(values)
        for func in self.class_method.matchers.match(matchable_, self.owner):
            return _dispatch(
                func,
                typing.cast(typing.Mapping, matchable_.matches),
                bound_args,
                bound_kwargs,
            )
        return self.class_method.__wrapped__(self.owner, *args, **kwargs)


class ClassMethodWhen(ClassMethodCall):
    """Wrapper class that exposes the ``when()`` decorators."""

    def when(
        self, /, **kwargs  # noqa: E225
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Add a binding for the wrapped method."""
        return self.class_method.when(**kwargs)


class StaticMethod(common.Descriptor):
    """Decorator with value-based dispatch. Acts as a classmethod."""

    __wrapped__: typing.Callable

    def __init__(self, func: typing.Callable) -> None:
        del func
        super().__init__()
        # A more specific annotation would be good, but that's waiting on
        # further development.
        self.matchers: common.MatchTemplate[typing.Any] = common.MatchTemplate()

    def __get__(self, instance, owner):
        if instance is None and common.owns(self, owner):
            return StaticMethodWhen(self)
        return StaticMethodCall(self)

    def when(
        self, /, **kwargs  # noqa: E225
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Add a binding for this function."""
        return common.decorate(self.matchers, _no_placeholder_kwargs(kwargs))


@_doc_wrapper.ProxyWrapper.wrap_class("static_method")
class StaticMethodCall:
    """Wrapper class that conceals the ``when()`` decorators."""

    def __init__(self, static_method: StaticMethod) -> None:
        self.static_method = static_method

    def __call__(
        self, /, *args: typing.Any, **kwargs: typing.Any  # noqa: E225
    ) -> typing.Any:
        bound_args, bound_kwargs, values = _bound_and_values(
            inspect.signature(self.static_method.__wrapped__), args, kwargs,
        )

        matchable_ = matchable.Matchable(values)
        for func in self.static_method.matchers.match(matchable_, None):
            return _dispatch(
                func,
                typing.cast(typing.Mapping, matchable_.matches),
                bound_args,
                bound_kwargs,
            )
        return self.static_method.__wrapped__(*args, **kwargs)


class StaticMethodWhen(StaticMethodCall):
    """Wrapper class that exposes the ``when()`` decorators."""

    def when(
        self, /, **kwargs: typing.Any  # noqa: E225
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Add a binding for the wrapped method."""
        return self.static_method.when(**kwargs)


class Function(common.Descriptor):
    """Decorator with value-based dispatch. Acts as a function."""

    __wrapped__: typing.Callable

    def __init__(self, func: typing.Callable) -> None:
        del func
        super().__init__()
        # A more specific annotation would be good, but that's waiting on
        # further development.
        self.matchers: common.MatchTemplate[typing.Any] = common.MatchTemplate()

    def __call__(
        self, /, *args: typing.Any, **kwargs: typing.Any  # noqa: E225
    ) -> typing.Any:
        # Okay, so, this is a convoluted mess.

        bound_args, bound_kwargs, values = _bound_and_values(
            inspect.signature(self), args, kwargs
        )

        instance = args[0] if args else None

        matchable_ = matchable.Matchable(values)
        for func in self.matchers.match_instance(matchable_, instance):
            return _dispatch(
                func,
                typing.cast(typing.Mapping, matchable_.matches),
                bound_args,
                bound_kwargs,
            )
        # Hey, we can just fall back now.
        return self.__wrapped__(*args, **kwargs)

    def __get__(self, instance: typing.Optional[T], owner: typing.Type[T]):
        if instance is None:
            if common.owns(self, owner):
                return self
            return MethodProxy(self)
        return functools.partial(self, instance)

    def when(
        self, /, **kwargs: typing.Any  # noqa: E225
    ) -> typing.Callable[[typing.Callable], typing.Callable]:
        """Add a binding for this function."""
        return common.decorate(self.matchers, _placeholder_kwargs(kwargs))


@_doc_wrapper.ProxyWrapper.wrap_class("func")
class MethodProxy:
    """Wrapper class that conceals the ``when()`` decorators."""

    def __init__(self, func: Function) -> None:
        self.func = func

    def __call__(
        self, /, *args: typing.Any, **kwargs: typing.Any  # noqa: E225
    ) -> typing.Any:
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner):
        return self.func.__get__(instance, owner)


def _kwarg_structure(kwargs: dict) -> mapping_match.DictPattern:
    return mapping_match.DictPattern(kwargs, exhaustive=True)


def _no_placeholder_kwargs(kwargs: Kwargs) -> common.Matcher:
    if any(
        isinstance(kwarg, _class_placeholder.Placeholder) for kwarg in kwargs.values()
    ):
        raise ValueError

    return _kwarg_structure(kwargs)


def _placeholder_kwargs(kwargs: Kwargs) -> common.Matcher:
    if any(
        isinstance(kwarg, _class_placeholder.Placeholder) for kwarg in kwargs.values()
    ):

        @_class_placeholder.Placeholder
        def _placeholder(cls: type) -> mapping_match.DictPattern:
            return _kwarg_structure(
                {
                    name: (
                        kwarg.func(cls)
                        if isinstance(kwarg, _class_placeholder.Placeholder)
                        else kwarg
                    )
                    for (name, kwarg) in kwargs.items()
                }
            )

        return _placeholder

    return _kwarg_structure(kwargs)
