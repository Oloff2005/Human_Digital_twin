"""Strategies module for the minimal Hypothesis stub."""

class _FloatStrategy:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def example(self):
        return (self.min_value + self.max_value) / 2.0


def floats(min_value=0.0, max_value=1.0):
    return _FloatStrategy(min_value, max_value)

__all__ = ["floats"]
