"""Utility functions for loading configuration files."""

from typing import Dict, Any
import os

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None


def load_baseline_state(path: str = "data/baseline_states.yaml") -> Dict[str, Any]:
    """Load default physiological state values from a YAML file.

    Parameters
    ----------
    path : str
        Path to the baseline YAML file.

    Returns
    -------
    Dict[str, Any]
        Dictionary mapping state variable names to their baseline values.
    """
    if not os.path.exists(path):
        return {}

    if yaml is not None:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    from hdt.config_loader import _simple_yaml_load

    return _simple_yaml_load(path)