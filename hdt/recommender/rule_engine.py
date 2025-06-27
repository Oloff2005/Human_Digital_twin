from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from .recommender import Recommender


# ---------------------------------------------------------------------------
# Machine learning placeholder
# ---------------------------------------------------------------------------
def predict_recommendations(state_dict: Dict[str, Any]) -> List[str]:
    """Return mock recommendations based on the provided state."""
    suggestions = [
        "Stay hydrated",
        "Consider a short walk",
        "Take deep breaths",
    ]
    if not suggestions:
        return []
    return [random.choice(suggestions)]


class RuleEngine:
    """Provide recommendations using either rule-based or ML-based logic."""

    def __init__(
        self,
        mode: str = "rule_based",
        rules_path: Optional[str] = None,
        rule_version: Optional[str] = None,
    ) -> None:
        if mode not in {"rule_based", "ml_based"}:
            raise ValueError(f"Unsupported mode '{mode}'")
        self.mode = mode
        self.rule_version = rule_version
        self.rules_path = rules_path

        if self.mode == "rule_based":
            if not self.rules_path:
                raise ValueError("rules_path must be provided for rule_based mode")
            self._engine = Recommender(self.rules_path, rule_version=self.rule_version)
        else:
            self._engine = None

    # ------------------------------------------------------------------
    def get_recommendations(self, state_dict: Dict[str, Any]) -> List[str]:
        """Return recommendations using the configured engine."""
        if self.mode == "rule_based" and self._engine is not None:
            return self._engine.recommend(state_dict)
        return predict_recommendations(state_dict)