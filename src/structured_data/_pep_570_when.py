import functools
import inspect


def pep_570_when(func):
    signature = inspect.signature(func)
    non_kwargs_only = dict(signature.parameters)
    kwargs = non_kwargs_only.pop(tuple(non_kwargs_only)[-1])

    parameters = [
        param.replace(kind=inspect.Parameter.POSITIONAL_ONLY)
        for param in non_kwargs_only.values()
    ]

    parameters.append(kwargs.replace(kind=inspect.Parameter.VAR_KEYWORD))

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, kwargs)

    wrapped.__signature__ = signature.replace(parameters=parameters)
    return wrapped
