from __future__ import annotations

import typing

from . import match_dict
from . import match_failure


class Matchable:
    """Given a value, attempt to match against a target.

    The truthiness of ``Matchable`` values varies on whether they have bindings
    associated with them. They are truthy exactly when they have bindings.

    ``Matchable`` values provide two basic forms of syntactic sugar.
    ``m_able(target)`` is equivalent to ``m_able.match(target)``, and
    ``m_able[k]`` will return ``m_able.matches[k]`` if the ``Matchable`` is
    truthy, and raise a ``ValueError`` otherwise.
    """

    value: typing.Any
    matches: typing.Optional[match_dict.MatchDict]

    def __init__(self, value: typing.Any):
        self.value = value
        self.matches = None

    def match(self, target) -> Matchable:
        """Match against target, generating a set of bindings."""
        try:
            self.matches = match_dict.match(target, self.value)
        except match_failure.MatchFailure:
            self.matches = None
        return self

    def __call__(self, target) -> Matchable:
        return self.match(target)

    def __getitem__(self, key):
        if self.matches is None:
            raise ValueError
        return self.matches[key]

    def __bool__(self):
        return self.matches is not None
