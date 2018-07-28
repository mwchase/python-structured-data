import keyword

DISCARD = object()


class Pattern(tuple):
    """A matcher that binds a value to a name."""

    __slots__ = ()

    def __new__(cls, name: str):
        if name == "_":
            return DISCARD
        if not name.isidentifier():
            raise ValueError
        if keyword.iskeyword(name):
            raise ValueError
        return super().__new__(cls, (name,))

    @property
    def name(self):
        """Return the name of the matcher."""
        return tuple.__getitem__(self, 0)

    def __getitem__(self, other):
        return AsPattern(self, other)


class AsPattern(tuple):
    """A matcher that contains further bindings."""

    __slots__ = ()

    def __new__(cls, matcher: Pattern, match):
        if match is DISCARD:
            return matcher
        return super().__new__(cls, (matcher, match))

    @property
    def matcher(self):
        """Return the left-hand-side of the as-match."""
        return self[0]

    @property
    def match(self):
        """Return the right-hand-side of the as-match."""
        return self[1]


class AttrPattern(tuple):

    __slots__ = ()

    def __new__(*args, **kwargs):
        cls, *args = args
        if args:
            raise ValueError(args)
        return super(AttrPattern, cls).__new__(cls, (tuple(kwargs.items()),))

    @property
    def match_dict(self):
        return self[0]


class DictPattern(tuple):

    __slots__ = ()

    def __new__(cls, match_dict, *, exhaustive=False):
        return super(DictPattern, cls).__new__(
            cls, (tuple(match_dict.items()), exhaustive)
        )

    @property
    def match_dict(self):
        return self[0]

    @property
    def exhaustive(self):
        return self[1]
