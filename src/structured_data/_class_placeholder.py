"""Functions for representing placeholders, which are used in abstract matchers."""

import typing

T_co = typing.TypeVar("T_co", covariant=True)  # pylint: disable=invalid-name


class Placeholder(typing.Generic[T_co]):
    """Class for representing placeholder functions."""

    def __init__(self, func: typing.Callable[[type], T_co]):
        self.func = func
