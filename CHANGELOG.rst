
Changelog
=========

Unreleased
----------

0.4.0 (2018-07-21)
------------------

Added
~~~~~

- Mapping class especially for match values. It's capable of quickly and concisely pulling out groups of variables, but it also properly supports extracting just a single value.
- Mapping class can now index from a ``dict`` to a ``dict``, in order to support ``**kwargs`` unpacking.

Fixed
~~~~~

- A bug (not present in any released version) that caused the empty tuple target to accept any tuple value. This is included partly because this was just such a weird bug.

Removed
~~~~~~~

- Unpublished the ``MatchFailure`` exception type, and the ``desugar`` function.

0.3.0 (2018-07-15)
------------------

Added
~~~~~

- Simpler way to create match bindings.
- Dependency on the ``astor`` library.
- First attempt at populating the annotations and signature of the generated constructors.
- ``data`` module containing some generic algebraic data types.
- Attempts at monad implementations for ``data`` classes.

Changed
~~~~~~~

- Broke the package into many smaller modules.
- Switched many attributes to use a ``WeakKeyDictionary`` instead.
- Moved prewritten methods into a class to avoid defining reserved methods at the module level.
- When assigning equality methods is disabled for a decorated class, the default behavior is now ``object`` semantics, rather than failing comparison and hashing with a ``TypeError``.
- The prewritten comparison methods no longer return ``NotImplemented``.

Removed
~~~~~~~

- Ctor metaclass.

0.2.1 (2018-07-13)
------------------

Fixed
~~~~~

- Removed an incorrect classifier. This code cannot run on pypy.

0.2.0 (2018-07-13)
------------------

Added
~~~~~

- Explicit ``__bool__`` implementation, to consider all constructor instances as truthy, unless defined otherwise.
- Python 3.7 support.

Changed
~~~~~~~

- Marked the enum constructor base class as private. (``EnumConstructor`` -> ``_EnumConstructor``)
- Switched scope of test coverage to supported versions. (Python 3.7)

Removed
~~~~~~~

- Support for Python 3.6 and earlier.
- Incidental functionality required by supported Python 3.6 versions. (Hooks to enable restricted subclassing.)

0.1.0 (2018-06-10)
------------------

- First release on PyPI.
