"""Temporary measure to hack in PEP 570-like behavior.

Will drop this module once I stop supporting Python 3.7.
"""

import functools
import inspect


def pep_570_when(func):
    """This function exists because I don't live in the future.

    It is awful, and its existence single-handedly justifies the effort put
    into writing up and implementing PEP 570.

    It is also not generally applicable, being tuned for exactly the use-case
    I wrote it for.
    """
    signature = inspect.signature(func)

    parameters = [
        param.replace(kind=inspect.Parameter.POSITIONAL_ONLY)
        for param in signature.parameters.values()
    ]

    parameters[-1] = parameters[-1].replace(kind=inspect.Parameter.VAR_KEYWORD)

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, kwargs)

    wrapped.__signature__ = signature.replace(parameters=parameters)
    return wrapped
