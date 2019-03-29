from .._not_in import not_in
from .basic_patterns import Pattern
from .compound_match import CompoundMatch


class Bind(CompoundMatch, tuple):
    """A wrapper that adds additional bindings to a successful match.

    The ``Bind`` constructor takes a single required argument, and any number
    of keyword arguments. The required argument is a matcher. When matching, if
    the match succeeds, the ``Bind`` instance adds bindings corresponding to
    its keyword arguments.
    """

    __slots__ = ()

    def __new__(*args, **kwargs):
        cls, structure = args
        if not kwargs:
            return structure
        not_in(kwargs, "_")
        return super(Bind, cls).__new__(cls, (structure, tuple(kwargs.items())))

    @property
    def structure(self):
        return self[0]

    @property
    def bindings(self):
        return self[1]

    def destructure(self, value):
        if value is self:
            return [Pattern(name) for (name, _) in reversed(self.bindings)] + [
                self.structure
            ]
        return [binding_value for (_, binding_value) in reversed(self.bindings)] + [
            value
        ]
