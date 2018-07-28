import keyword
import typing

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


class MultiDestructPattern(tuple):

    __slots__ = ()

    args_class = None

    def __new__(*args, **kwargs):
        cls, *args = args
        args_ = cls.args_class()
        if args:
            args_, = args
        if not isinstance(args_, cls.args_class):
            raise ValueError(args_)
        return super(MultiDestructPattern, cls).__new__(cls, (tuple(kwargs.items()), args_))

    def alter(self, **kwargs):
        return type(self)(self[1]._replace(**kwargs), **dict(self[0]))

    @property
    def match_dict(self):
        return self[0]


class AttrArgs(typing.NamedTuple):

    pass


class AttrPattern(MultiDestructPattern):

    __slots__ = ()

    args_class = AttrArgs


class DictArgs(typing.NamedTuple):

    exhaustive: bool = False


class DictPattern(MultiDestructPattern):

    __slots__ = ()

    args_class = DictArgs

    @property
    def exhaustive(self):
        return self[1].exhaustive
