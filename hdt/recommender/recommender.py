try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from typing import Any, Dict, List

from hdt.config_loader import _parse_scalar


def _simple_rules_load(path: str) -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#", 1)[0].rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("- "):
                if current:
                    rules.append(current)
                current = {}
                line = line[2:].strip()
                if line:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        current[key.strip()] = _parse_scalar(val.strip().strip('"').strip("'"))
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                current[key.strip()] = _parse_scalar(val.strip().strip('"').strip("'"))
    if current:
        rules.append(current)
    return rules


class Recommender:
    """Simple rule-based recommender."""

    def __init__(self, rules_path: str) -> None:
        if yaml is not None:
            with open(rules_path, "r", encoding="utf-8") as f:
                self.rules: List[Dict[str, Any]] = yaml.safe_load(f) or []
        else:
            self.rules = _simple_rules_load(rules_path)

    def recommend(self, state: Dict[str, Any]) -> Dict[str, List[str]]:
        suggestions: List[str] = []
        for rule in self.rules:
            cond = rule.get("condition")
            suggestion = rule.get("suggestion", "")
            if not cond:
                continue
            try:
                if eval(cond, {}, {"state": state}):
                    if suggestion:
                        suggestions.append(str(suggestion))
            except Exception:
                continue
        return {"suggestions": suggestions}
