
Changelog
=========

Unreleased
----------

Added
~~~~~

- Explicit ``__bool__`` implementation, to consider all constructor instances as truthy, unless defined otherwise.

Changed
~~~~~~~

- Marked the enum constructor base class as private. (``EnumConstructor`` -> ``_EnumConstructor``)
- Restricted scope of test coverage to versions with partial support. (Python 3.6)

0.1.0 (2018-06-10)
------------------

- First release on PyPI.
