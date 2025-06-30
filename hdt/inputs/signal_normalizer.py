from __future__ import annotations

import math
from typing import Any, Dict
from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class SignalNormalizer:
    def __init__(self) -> None:
        """
        Optionally initialize normalization parameters or scaling coefficients.
        """
        pass

    def normalize(self, parsed_signals: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Normalize all signal values by unit and signal name.

        Args:
            parsed_signals (dict): Output from InputParser with format:
                {
                    "BrainController": {"heart_rate": 72, ...},
                    "MuscleReactor": {"steps": 10432, ...},
                    ...
                }

        Returns:
            dict: Normalized signals in the same structure
        """
        normalized_signals: Dict[str, Dict[str, float]] = {}

        for unit, signals in parsed_signals.items():
            normalized_signals[unit] = {}

            for signal, value in signals.items():
                if value is None:
                    logger.warning("%s.%s is None; skipping", unit, signal)
                    continue
                if isinstance(value, (int, float)) and math.isnan(value):
                    logger.warning("%s.%s is NaN; skipping", unit, signal)
                    continue
                normalized_value = self._normalize_signal(signal, value)
                normalized_signals[unit][signal] = normalized_value

        return normalized_signals

    def _normalize_signal(self, signal: str, value: float) -> float:
        """
        Apply normalization logic based on signal name.

        You can scale values, clip outliers, or use model-specific ranges.

        Args:
            signal (str): The name of the input signal (e.g., "hrv")
            value (float): The raw value

        Returns:
            float: Normalized value (typically 0–1 range)
        """
        # Simple linear scaling based on typical expected ranges
        if signal == "heart_rate":
            return value / 100.0
        elif signal == "resting_heart_rate":
            return value / 100.0
        elif signal == "sleep_score":
            return value / 100.0
        elif signal == "training_readiness":
            return value / 100.0
        elif signal == "stress_score":
            return value / 100.0
        elif signal == "oxygen_saturation":
            return value / 100.0
        elif signal == "parasympathetic_tone":
            return value  # already 0–1
        else:
            return value  # fallback: no transformation
