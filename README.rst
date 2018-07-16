========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-structured-data/badge/?style=flat
    :target: https://readthedocs.org/projects/python-structured-data
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/mwchase/python-structured-data.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/mwchase/python-structured-data

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/mwchase/python-structured-data?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/mwchase/python-structured-data

.. |requires| image:: https://requires.io/github/mwchase/python-structured-data/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/mwchase/python-structured-data/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/mwchase/python-structured-data/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/mwchase/python-structured-data

.. |version| image:: https://img.shields.io/pypi/v/structured-data.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/structured-data

.. |commits-since| image:: https://img.shields.io/github/commits-since/mwchase/python-structured-data/v0.2.1.svg
    :alt: Commits since latest release
    :target: https://github.com/mwchase/python-structured-data/compare/v0.2.1...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/structured-data.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/structured-data

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/structured-data.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/structured-data

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/structured-data.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/structured-data


.. end-badges

Code generators for immutable structured data, including algebraic data types, and functions to destructure them.
Structured Data provides two public modules: :module:`structured_data.enum` and :module:`structured_data.match`.

The ``enum`` module provides a class decorator and annotation type for converting a class into an algebraic data type; the name is taken from its use in Rust.

The ``match`` module provides a ``Pattern`` class that can be used to build match structures, and a ``ValueMatcher`` class that wraps a value, and attempts to apply match structures to it.
If the match succeeds, the bindings can be extracted and used.
It includes some special support for ``enum`` subclasses.

The match architecture allows you tell pull values out of a nested structure:

.. code-block:: python3

    structure = (match.pat.a, match.pat.b @ (match.pat.c, match.pat.d), 5)
    my_value = (('abc', 'xyz'), ('def', 'ghi'), 5)
    value_matcher = match.ValueMatcher(my_value)
    if value_matcher.match(structure):
        # The format of the matches is not final.
        print(value_matcher.matches['a'])  # ('abc', 'xyz')
        print(value_matcher.matches['b'])  # ('def', 'ghi')
        print(value_matcher.matches['c'])  # 'def'
        print(value_matcher.matches['d'])  # 'ghi'

The ``@`` operator allows binding both the outside and the inside of a structure.
The contents of the ``matches`` attribute will change once there's been some real-world usage.

The ``enum`` decorator exists to create classes that do not necessarily have a single fixed format, but do have a fixed set of possible formats.
This lowers the maintenance burden of writing functions that operate on values of an ``enum`` class, because the full list of cases to handle is directly in the class definition.

Here are implementations of common algebraic data types in other languages:

.. code-block:: python3

    @enum.enum
    class Maybe(typing.Generic[T]):

        Just: enum.Ctor[T]
        Nothing: enum.Ctor

    @enum.enum
    class Result(typing.Generic[R, E]):

        Ok: enum.Ctor[R]
        Err: enum.Ctor[E]

* Free software: MIT license

Installation
============

::

    pip install structured-data

Documentation
=============

https://python-structured-data.readthedocs.io/

Development
===========

To run the all tests run::

    tox
