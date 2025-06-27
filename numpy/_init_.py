"""Minimal numpy stub providing only isnan for tests."""

def isnan(x):
    try:
        return x != x
    except Exception:
        return False