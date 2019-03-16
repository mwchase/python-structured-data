from .._match_failure import MatchFailure
from .basic_patterns import DISCARD
from .compound_match import CompoundMatch


class Guard(CompoundMatch, tuple):

    __slots__ = ()

    def __new__(cls, guard, structure=DISCARD) -> CompoundMatch:
        if structure is not DISCARD:
            return AsGuard(Guard(guard), structure)
        return super().__new__(cls, (guard,))

    def __getitem__(self, key):
        return AsGuard(self, key)

    @property
    def guard(self):
        return tuple.__getitem__(self, 0)

    def destructure(self, value):
        if value is self or self.guard(value):
            return ()
        raise MatchFailure


class AsGuard(CompoundMatch, tuple):

    __slots__ = ()

    def __new__(cls, base_guard, structure) -> CompoundMatch:
        if structure is DISCARD:
            return base_guard
        return super().__new__(cls, (base_guard, structure))

    @property
    def guard(self):
        return self[0].guard

    @property
    def structure(self):
        return self[1]

    def destructure(self, value):
        if value is self:
            return (self.structure,)
        if self.guard(value):
            return (value,)
        raise MatchFailure
