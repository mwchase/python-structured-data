"""Abstract base class for advanced match classes."""


class CompoundMatch:
    """Abstract base class for advanced match classes."""

    __slots__ = ()

    def destructure(self, value):
        """Given a value, return a sequence of values extracted from the match.

        Usually has special-case behavior when ``value is self``, possibly as
        part of a broader conditional that happens to be true in that specific
        case as well.
        """
        raise NotImplementedError
