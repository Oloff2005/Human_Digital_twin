try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from typing import Any, Dict, List, Union

from hdt.config_loader import _parse_scalar


def _simple_rules_load(
    path: str,
) -> Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Very small loader supporting lists of rule dicts optionally grouped by version."""

    versions: Dict[str, List[Dict[str, Any]]] = {}
    root_rules: List[Dict[str, Any]] = []
    current_rule: Dict[str, Any] = {}
    current_target: List[Dict[str, Any]] = root_rules

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#", 1)[0].rstrip("\n")
            if not line.strip():
                continue

            indent = len(raw) - len(raw.lstrip(" "))
            content = line.strip()

            if indent == 0 and content.endswith(":") and not content.startswith("-"):
                if current_rule:
                    current_target.append(current_rule)
                    current_rule = {}
                version = content[:-1]
                current_target = versions.setdefault(version, [])
                continue

            if content.startswith("- "):
                if current_rule:
                    current_target.append(current_rule)
                current_rule = {}
                content = content[2:].strip()
                if content and ":" in content:
                    key, val = content.split(":", 1)
                    current_rule[key.strip()] = _parse_scalar(
                        val.strip().strip('"').strip("'")
                    )
                continue

            if ":" in content:
                key, val = content.split(":", 1)
                current_rule[key.strip()] = _parse_scalar(
                    val.strip().strip('"').strip("'")
                )

    if current_rule:
        current_target.append(current_rule)

    if versions:
        if root_rules:
            versions["default"] = root_rules
        return versions
    return root_rules


class Recommender:
    """Simple rule-based recommender with optional A/B rule versions."""

    def __init__(self, rules_path: str, rule_version: str | None = None) -> None:
        self.rule_version = rule_version

        if yaml is not None:
            with open(rules_path, "r", encoding="utf-8") as f:
                data: Union[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]] = (
                    yaml.safe_load(f) or {}
                )
        else:
            data = _simple_rules_load(rules_path)

        if isinstance(data, list):
            self.rules = data
        elif isinstance(data, dict):
            if self.rule_version is None:
                if len(data) == 1:
                    self.rule_version, self.rules = next(iter(data.items()))
                else:
                    raise ValueError(
                        "rule_version must be specified when multiple versions are present"
                    )
            else:
                if self.rule_version not in data:
                    raise ValueError(f"Unknown rule_version '{self.rule_version}'")
                self.rules = data[self.rule_version]
        else:
            self.rules = []

    def recommend(self, state: Dict[str, Any]) -> List[str]:
        """Return a list of suggestions based on the provided ``state``."""
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

        return suggestions

    def get_rules(self) -> List[Dict[str, Any]]:
        """Return the currently loaded rule set."""
        return self.rules

    def get_version(self) -> str | None:
        """Return the active rule version."""
        return self.rule_version


def threshold_rule_match(values: Dict[str, float], rules_path: str) -> List[str]:
    """Return recommendations based on numeric threshold rules."""
    if yaml is not None:
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = yaml.safe_load(f) or {}
    else:
        from hdt.config_loader import _simple_yaml_load

        rules = _simple_yaml_load(rules_path)

    suggestions: List[str] = []
    for metric, thresh in rules.items():
        if metric not in values:
            continue
        val = values[metric]

        high = thresh.get("high") if isinstance(thresh, dict) else None
        if isinstance(high, dict):
            t = high.get("threshold")
            try:
                if t is not None and val > float(t):
                    msg = high.get("message")
                    if msg:
                        suggestions.append(str(msg).strip('"').strip("'"))
            except (ValueError, TypeError):
                pass

        low = thresh.get("low") if isinstance(thresh, dict) else None
        if isinstance(low, dict):
            t = low.get("threshold")
            try:
                if t is not None and val < float(t):
                    msg = low.get("message")
                    if msg:
                        suggestions.append(str(msg).strip('"').strip("'"))
            except (ValueError, TypeError):
                pass

    return suggestions
