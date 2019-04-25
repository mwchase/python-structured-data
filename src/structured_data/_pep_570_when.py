import functools
import inspect


def pep_570_when(func):
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
