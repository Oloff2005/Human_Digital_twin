"""Circadian model producing sleep drive and melatonin release."""

import math
from typing import Any, Dict, Optional

from .base_unit import BaseUnit


class SleepRegulationCenter(BaseUnit):
    """Simulate circadian driven sleep pressure and recovery."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.drive_gain: float = float(config.get("drive_gain", 0.05))
        self.recovery_gain: float = float(config.get("recovery_gain", 0.1))
        self.melatonin_amplitude: float = float(config.get("melatonin_amplitude", 1.0))
        self.sleep_drive: float = float(config.get("initial_sleep_drive", 0.5))

        # Optional compatibility state
        self.hours_awake: float = 0.0

        self._override: Optional[float] = None

        # Optional override for real-time control
        self.override_inputs: Optional[Dict[str, Any]] = None

    def reset(self) -> None:
        """Reset sleep drive and overrides."""
        self.sleep_drive = 0.5
        self.hours_awake = 0.0
        self._override = None

    # ------------------------------------------------------------------
    # Legacy helpers ----------------------------------------------------
    def update_state(self, hours_since_last_sleep: float) -> None:
        """Maintain backwards compatibility with older API."""
        self.hours_awake = hours_since_last_sleep

    def compute_sleep_signals(
        self, current_hour: int, wearable_signals: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Wrapper using older interface for existing code paths."""
        wearable_signals = wearable_signals or {}
        circadian_phase = (current_hour % 24) / 24
        sleep_quality = wearable_signals.get(
            "sleep_quality", 1.0 - wearable_signals.get("sleep_debt", 0.0)
        )
        cortisol = wearable_signals.get("cortisol", 0.0)

        result = self.step(
            {
                "circadian_phase": circadian_phase,
                "sleep_quality": sleep_quality,
                "cortisol": cortisol,
            }
        )
        # include legacy outputs
        result["sleep_drive"] = round(self.sleep_drive, 3)
        result["sleep_signal"] = round(
            result["melatonin"] * 0.7 + result["recovery_score"] * 0.3, 3
        )
        return result

    # ------------------------------------------------------------------
    def set_sleep_drive_override(self, value: float) -> None:
        """Allow real-time override of the sleep drive state."""
        self._override = value

    def clear_override(self) -> None:
        self._override = None

    def inject_override(self, inputs: Dict[str, Any]) -> None:
        """Store override inputs for the next :meth:`step` call."""
        self.override_inputs = inputs

    # ------------------------------------------------------------------
    def _calculate_melatonin(self, circadian_phase: float) -> float:
        phase = circadian_phase % 1.0
        mel = 0.5 * (1 + math.cos(2 * math.pi * (phase - 0.5)))
        return min(1.0, max(0.0, mel * self.melatonin_amplitude))

    def compute_derivatives(
        self,
        state: Dict[str, float],
        circadian_phase: float,
        sleep_quality: float,
        cortisol: float,
    ) -> Dict[str, float]:
        melatonin = self._calculate_melatonin(circadian_phase)
        increase = self.drive_gain * (1 - melatonin)
        decrease = self.recovery_gain * sleep_quality * melatonin
        cortisol_effect = cortisol * 0.05
        d_drive = increase - decrease + cortisol_effect
        return {"sleep_drive": d_drive}

    def get_state(self) -> Dict[str, float]:
        return {"sleep_drive": self.sleep_drive}

    def set_state(self, state_dict: Dict[str, float]) -> None:
        self.sleep_drive = state_dict.get("sleep_drive", self.sleep_drive)

    def step(self, inputs: Dict[str, Any]) -> Dict[str, float]:
        circadian_phase = float(inputs.get("circadian_phase", 0.0))
        sleep_quality = float(inputs.get("sleep_quality", 1.0))
        cortisol = float(inputs.get("cortisol", 0.0))
        if self.override_inputs is not None:
            o = self.override_inputs
            circadian_phase = o.get("circadian_phase", circadian_phase)
            sleep_quality = o.get("sleep_quality", sleep_quality)
            cortisol = o.get("cortisol", cortisol)
            self.override_inputs = None

        melatonin = self._calculate_melatonin(circadian_phase)

        if self._override is not None:
            self.sleep_drive = self._override
        else:
            deriv = self.compute_derivatives(
                {"sleep_drive": self.sleep_drive},
                circadian_phase,
                sleep_quality,
                cortisol,
            )["sleep_drive"]
            self.sleep_drive = min(1.0, max(0.0, self.sleep_drive + deriv))

        recovery_score = max(0.0, 1.0 - self.sleep_drive)

        return {
            "melatonin": round(melatonin, 3),
            "recovery_score": round(recovery_score, 3),
        }
