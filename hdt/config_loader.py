"""Utility functions to load YAML configuration files for the simulator."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, cast

try:
    import yaml  # type: ignore
    yaml_lib = yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency may be absent
    yaml_lib = None


def _parse_scalar(value: str) -> Any:
    """Parse a YAML scalar into the appropriate Python type."""
    lower = value.lower()
    if lower in {"true", "false"}:
        return lower == "true"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _simple_yaml_load(path: str) -> Dict[str, Any]:
    """Very small YAML loader supporting the subset used in tests."""
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Any]] = [(0, root)]  # (indent, container)
    key_stack: List[str] = []  # track keys for dict containers

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#", 1)[0].rstrip("\n")
            if not line.strip():
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            content = line.strip()

            while stack and indent < stack[-1][0]:
                stack.pop()
                if len(key_stack) >= len(stack):
                    key_stack.pop()

            parent = stack[-1][1]

            if content.startswith("- "):
                value = _parse_scalar(content[2:].strip())
                if isinstance(parent, list):
                    parent.append(value)
                elif parent == {} and key_stack:
                    key = key_stack[-1]
                    grandparent = stack[-2][1]
                    lst: List[Any] = []
                    grandparent[key] = lst
                    stack[-1] = (indent, lst)
                    parent = lst
                    parent.append(value)
                else:
                    raise ValueError(f"Unexpected list item: {content}")
            else:
                key, rest = content.split(":", 1)
                key = key.strip()
                rest = rest.strip()
                if rest == "":
                    new_container: Dict[str, Any] = {}
                    parent[key] = new_container
                    stack.append((indent + 2, new_container))
                    key_stack.append(key)
                else:
                    parent[key] = _parse_scalar(rest)
    return root


def load_units_config(path: str) -> Dict[str, Any]:
    """Load unit configuration YAML."""
    if yaml_lib is not None:
        with open(path, "r", encoding="utf-8") as f:
            return cast(Dict[str, Any], yaml_lib.safe_load(f))
    return _simple_yaml_load(path)


def load_sim_params(path: str) -> Dict[str, Any]:
    """Load simulator parameter YAML."""
    if yaml_lib is not None:
        with open(path, "r", encoding="utf-8") as f:
            return cast(Dict[str, Any], yaml_lib.safe_load(f))
    return _simple_yaml_load(path)
