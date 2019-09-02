import typing

_K = typing.TypeVar("_K")
_V = typing.TypeVar("_V")


def nillable_write(dct: typing.Dict[_K, _V], key: _K, value: typing.Optional[_V]):
    if value is None:
        dct.pop(key, typing.cast(_V, None))
    else:
        dct[key] = value
