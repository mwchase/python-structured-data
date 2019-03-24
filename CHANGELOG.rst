
Changelog
=========

0.11.1 (2019-03-23)
-------------------

Changed
~~~~~~~

- Restore proper behavior of ``__new__`` overrides.

0.11.0 (2019-03-23)
-------------------

Changed
~~~~~~~

- Consider all overrides of checked dunder methods, not just those in the decorated class.

0.10.1 (2019-03-22)
-------------------

Added
~~~~~

- A non-ergonomic but simple wrapper class for use by the typing plugin. It's not available to runtime code.

0.10.0 (2019-03-21)
-------------------

Changed
~~~~~~~

- Actually, the facade was working, I was just confused. Restored the facade.

0.9.0 (2019-03-20)
------------------

Changed
~~~~~~~

- Removed the facade.
- Added stability guarantee to Ctor.

0.8.0 (2019-03-19)
------------------

Changed
~~~~~~~

- Rewrote the facade.

0.7.0 (2019-03-19)
------------------

Changed
~~~~~~~

- Tried to put up a facade for type analysis. It didn't work.

0.6.1 (2019-03-18)
------------------

Added
~~~~~

- ``Bind`` class for attaching extra data to a match structure.
- PEP 561 support.

Changed
~~~~~~~

- As-patterns are now formed with indexing instead of the ``@`` operator.
- ``AttrPattern`` and ``DictPattern`` now take keyword arguments instead of a ``dict`` argument, and form new versions of themselves with an ``alter`` method.
- Actually. Change ``DictPattern`` back, stop trying to keep these things in synch.

0.6.0 (2018-07-27)
------------------

Added
~~~~~

- ``AttrPattern`` and ``DictPattern`` classes that take a ``dict`` argument and perform destructuring match against arbitrary objects, and mappings, respectively.

Changed
~~~~~~~

- Added special handling for matching AsPatterns against different AsPatterns. This is subject to change, as it's definitely an edge case.

0.5.0 (2018-07-22)
------------------

Added
~~~~~

- ``Matchable`` class is now callable and indexable. Calling is forwarded to the ``match`` method, and indexing forwards to the ``matches`` attribute, if it exists, and raises an error otherwise.
- ``Matchable`` class now has custom coercion to bool: ``False`` if the last match attempt failed, ``True`` otherwise.

Changed
~~~~~~~

- Renamed ``enum`` to ``adt`` to avoid confusion.
- Renamed ``ValueMatcher`` to ``Matchable``.
- ``Matchable.match`` now returns the ``Matchable`` instance, which can then be coerced to ``bool``, or indexed directly.

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
