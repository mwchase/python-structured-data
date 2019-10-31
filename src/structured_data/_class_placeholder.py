"""Functions for representing placeholders, which are used in abstract matchers."""

import typing

import typing_extensions

T_co = typing.TypeVar("T_co", covariant=True)  # pylint: disable=invalid-name


class Placeholder(typing_extensions.Protocol, typing.Generic[T_co]):
    """Protocol class for representing placeholder functions."""

    def __call__(self, type_: type) -> T_co:
        ...  # pragma: nocover

    is_placeholder: bool = True


def placeholder(function: typing.Callable[[type], T_co]) -> Placeholder[T_co]:
    """Convert the given function to a placeholder."""
    result = typing.cast(Placeholder, function)
    result.is_placeholder = True
    return result


def is_placeholder(function: typing.Any) -> bool:
    """Return whether the given function is a placeholder."""
    return getattr(function, "is_placeholder", False)
