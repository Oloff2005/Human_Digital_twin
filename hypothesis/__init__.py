"""Minimal stub of the Hypothesis API used in tests."""

from .strategies import floats


def given(**kwargs):
    """Simplistic decorator that calls the test once with example values."""

    def decorator(fn):
        def wrapper(*args, **kw):
            generated = {name: strat.example() for name, strat in kwargs.items()}
            return fn(*args, **generated, **kw)

        return wrapper

    return decorator

__all__ = ["given", "floats"]
