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
        | |codacy| |codebeat| |codeclimate| |scrutinizer|
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

.. |codacy| image:: https://api.codacy.com/project/badge/Grade/1a9e4a5640b446768c21a87d3566d33e
    :target: https://www.codacy.com/app/max-chase/python-structured-data?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mwchase/python-structured-data&amp;utm_campaign=Badge_Grade

.. |codebeat| image:: https://codebeat.co/badges/de1fa625-e4d4-4e11-bf94-ee9b4a0acf91
    :target: https://codebeat.co/projects/github-com-mwchase-python-structured-data-master
    :alt: Codebeat Code Quality Status

.. |codeclimate| image:: https://api.codeclimate.com/v1/badges/535f66af50b72ee28e62/maintainability
    :target: https://codeclimate.com/github/mwchase/python-structured-data/maintainability
    :alt: Code Climate Maintainability Score

.. |scrutinizer| image:: https://scrutinizer-ci.com/g/mwchase/python-structured-data/badges/quality-score.png?b=master
    :target: https://scrutinizer-ci.com/g/mwchase/python-structured-data/?branch=master
    :alt: Scrutinizer Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/structured-data.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/structured-data

.. |commits-since| image:: https://img.shields.io/github/commits-since/mwchase/python-structured-data/v0.11.0.svg
    :alt: Commits since latest release
    :target: https://github.com/mwchase/python-structured-data/compare/v0.11.0...master

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
Structured Data provides three public modules: ``structured_data.adt``, ``structured_data.match``, and ``structured_data.data``.

The ``adt`` module provides a class decorator and annotation type for converting a class into an algebraic data type.

The ``match`` module provides a ``Pattern`` class that can be used to build match structures, and a ``Matchable`` class that wraps a value, and attempts to apply match structures to it.
If the match succeeds, the bindings can be extracted and used.
It includes some special support for ``adt`` subclasses.

The match architecture allows you tell pull values out of a nested structure:

.. code-block:: python3

    structure = (match.pat.a, match.pat.b[match.pat.c, match.pat.d], 5)
    my_value = (('abc', 'xyz'), ('def', 'ghi'), 5)
    matchable = match.Matchable(my_value)
    if matchable(structure):
        # The format of the matches is not final.
        print(matchable['a'])  # ('abc', 'xyz')
        print(matchable['b'])  # ('def', 'ghi')
        print(matchable['c'])  # 'def'
        print(matchable['d'])  # 'ghi'

The ``@`` operator allows binding both the outside and the inside of a structure.
Indexing is forwarded to a ``matches`` attribute, which is ``None`` if the last match was not successful, and otherwise contains an instance of a custom mapping type, which allows building the matched values back up into simple structures.

The ``adt`` decorator exists to create classes that do not necessarily have a single fixed format, but do have a fixed set of possible formats.
This lowers the maintenance burden of writing functions that operate on values of an ``adt`` class, because the full list of cases to handle is directly in the class definition.

Here are implementations of common algebraic data types in other languages:

.. code-block:: python3

    @adt.adt
    class Maybe(typing.Generic[T]):

        Just: adt.Ctor[T]
        Nothing: adt.Ctor

    @adt.adt
    class Either(typing.Generic[E, R]):

        Left: adt.Ctor[E]
        Right: adt.Ctor[R]

The ``data`` module provides classes based on these examples.

* Free software: MIT license

Should I Use This?
==================

Until there's a major version out, probably not.

There are several alternatives in the standard library that may be better suited to particular use-cases:

- The ``namedtuple`` factory creates tuple classes with a single structure; the ``typing.NamedTuple`` class offers the ability to include type information. The interface is slightly awkward, and the values expose their tuple-nature easily. (NOTE: In Python 3.8, the fast access to namedtuple members means that they bypass user-defined ``__getitem__`` methods, thereby allowing factory consumers to customize indexing without breaking attribute access. It looks like it does still rely on iteration behavior for various convenience methods.)
- The ``enum`` module provides base classes to create finite enumerations. Unlike NamedTuple, the ability to convert values into an underlying type must be opted into in the class definition.
- The ``dataclasses`` module provides a class decorator that converts a class into one with a single structure, similar to a namedtuple, but with more customization: instances are mutable by default, and it's possible to generate implementations of common protocols.
- The Structured Data ``adt`` decorator is inspired by the design of ``dataclasses``. (A previous attempt used metaclasses inspired by the ``enum`` module, and was a nightmare.) Unlike ``enum``, it doesn't require all instances to be defined up front; instead each class defines constructors using a sequence of types, which ultimately determines the number of arguments the constructor takes. Unlike ``namedtuple`` and ``dataclasses``, it allows instances to have multiple shapes with their own type signatures. Unlike using regular classes, the set of shapes is specified up front.
- If you want multiple shapes, and don't want to specify them ahead of time, your best bet is probably a normal tree of classes, where the leaf classes are ``dataclasses``.

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
