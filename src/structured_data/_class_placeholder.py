def placeholder(function):
    function.is_placeholder = True
    return function


def is_placeholder(function) -> bool:
    return getattr(function, "is_placeholder", False)
