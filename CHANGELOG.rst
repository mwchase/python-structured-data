
Changelog
=========

Unreleased
----------

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
