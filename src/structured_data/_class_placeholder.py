import typing

import typing_extensions

T_co = typing.TypeVar("T_co", covariant=True)


class Placeholder(typing_extensions.Protocol, typing.Generic[T_co]):
    def __call__(self, type: type) -> T_co:
        ...  # pragma: nocover

    is_placeholder: bool = True


def placeholder(function: typing.Callable[[type], T_co]) -> Placeholder[T_co]:
    result = typing.cast(Placeholder, function)
    result.is_placeholder = True
    return result


def is_placeholder(function: typing.Any) -> bool:
    return getattr(function, "is_placeholder", False)
