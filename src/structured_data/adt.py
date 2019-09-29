"""Base classes for defining abstract data types.

This module provides three public members, which are used together.

Given a structure, possibly a choice of different structures, that you'd like
to associate with a type:

- First, create a class, that subclasses the Sum class.
- Then, for each possible structure, add an attribute annotation to the class
  with the desired name of the constructor, and a type of ``Ctor``, with the
  types within the constructor as arguments.

To look inside an ADT instance, use the functions from the
:mod:`structured_data.match` module.

Putting it together:

>>> from structured_data import match
>>> class Example(Sum):
...     FirstConstructor: Ctor[int, str]
...     SecondConstructor: Ctor[bytes]
...     ThirdConstructor: Ctor
...     def __iter__(self):
...         matchable = match.Matchable(self)
...         if matchable(Example.FirstConstructor(match.pat.count, match.pat.string)):
...             count, string = matchable[match.pat.count, match.pat.string]
...             for _ in range(count):
...                 yield string
...         elif matchable(Example.SecondConstructor(match.pat.bytes)):
...             bytes_ = matchable[match.pat.bytes]
...             for byte in bytes_:
...                 yield chr(byte)
...         elif matchable(Example.ThirdConstructor()):
...             yield "Third"
...             yield "Constructor"
>>> list(Example.FirstConstructor(5, "abc"))
['abc', 'abc', 'abc', 'abc', 'abc']
>>> list(Example.SecondConstructor(b"abc"))
['a', 'b', 'c']
>>> list(Example.ThirdConstructor())
['Third', 'Constructor']
"""

import typing

from ._adt.product_type import Product
from ._adt.sum_type import Sum

if typing.TYPE_CHECKING:  # pragma: nocover

    T = typing.TypeVar("T")

    class Ctor:
        """Dummy class for type-checking purposes."""

    class ConcreteCtor(typing.Generic[T]):
        """Wrapper class for type-checking purposes.

        The type parameter should be a Tuple type of fixed size.
        Classes containing this annotation (meaning they haven't been
        processed by the ``adt`` decorator) should not be instantiated.
        """


else:
    from ._adt.ctor import Ctor


__all__ = ["Ctor", "Product", "Sum"]
