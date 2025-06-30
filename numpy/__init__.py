"""Minimal numpy stub providing small subset of functionality used in tests."""
from typing import Iterable, List
import builtins
import math


def isnan(x: float) -> bool:
    try:
        return x != x
    except Exception:
        return False


def asarray(seq: Iterable[float], dtype: type | None = None) -> List[float]:
    return [float(x) for x in seq]


def mean(seq: Iterable[float]) -> float:
    values = [float(x) for x in seq]
    return sum(values) / len(values) if values else 0.0


def sqrt(x: float) -> float:
    return math.sqrt(x)


def abs(x: float) -> float:
    return builtins.abs(x)
