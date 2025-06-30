"""ODE-compatible model of glycogen and fat energy storage."""

from typing import Any, Dict, Optional

from .base_unit import BaseUnit


class FatStorageReservoir(BaseUnit):
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        ODE-compatible energy storage unit for glycogen and fat.

        Args:
            config (dict): {
                - max_glycogen (g)
                - max_fat (g)
                - mobilization_rate (g/hr)
                - initial_glycogen (g)
                - initial_fat (g)
            }
        """
        self.max_glycogen = config.get("max_glycogen", 400)
        self.max_fat = config.get("max_fat", 12000)
        self.mobilization_rate = config.get("mobilization_rate", 60)

        self.current_glycogen = config.get("initial_glycogen", 300)
        self.current_fat = config.get("initial_fat", 8000)

        # External inputs for dynamic routing
        self._storage_inputs = {"glycogen_stored": 0.0, "fat_stored": 0.0}
        self._glucagon_signal = 0.5

    def reset(self) -> None:
        """Reset stored nutrient amounts."""
        self.current_glycogen = 0.0
        self.current_fat = 0.0
        self._storage_inputs = {"glycogen_stored": 0.0, "fat_stored": 0.0}
        self._glucagon_signal = 0.5

    def load_inputs(
        self,
        storage_inputs: Optional[Dict[str, float]] = None,
        glucagon_signal: float = 0.5,
    ) -> None:
        self._storage_inputs = storage_inputs or {
            "glycogen_stored": 0.0,
            "fat_stored": 0.0,
        }
        self._glucagon_signal = glucagon_signal

    def get_state(self) -> Dict[str, float]:
        return {
            "storage_glycogen": self.current_glycogen,
            "storage_fat": self.current_fat,
        }

    def set_state(self, state_dict: Dict[str, float]) -> None:
        self.current_glycogen = state_dict["storage_glycogen"]
        self.current_fat = state_dict["storage_fat"]

    def derivatives(self, t: float, state: Dict[str, float]) -> Dict[str, float]:
        """
        ODE model for dynamic storage and mobilization:
        d(storage) = +input - mobilization
        """
        glycogen_in = self._storage_inputs.get("glycogen_stored", 0.0)
        fat_in = self._storage_inputs.get("fat_stored", 0.0)

        # Max mobilizable per hour, scaled by signal
        max_mobilize = self.mobilization_rate * self._glucagon_signal
        glycogen_out = min(max_mobilize * 0.5, state["storage_glycogen"])
        fat_out = min(max_mobilize * 0.5, state["storage_fat"])

        d_glycogen_dt = glycogen_in - glycogen_out
        d_fat_dt = fat_in - fat_out

        return {"storage_glycogen": d_glycogen_dt, "storage_fat": d_fat_dt}

    # Discrete versions for compatibility/testing
    def store(self, inputs: Dict[str, float]) -> Dict[str, float]:
        self.current_glycogen = min(
            self.max_glycogen, self.current_glycogen + inputs.get("glycogen_stored", 0)
        )
        self.current_fat = min(
            self.max_fat, self.current_fat + inputs.get("fat_stored", 0)
        )
        return {"glycogen": self.current_glycogen, "fat": self.current_fat}

    def mobilize(
        self, signal_strength: float = 0.5, duration_hr: float = 1.0
    ) -> Dict[str, Dict[str, float]]:
        max_mobilize = self.mobilization_rate * duration_hr * signal_strength
        glycogen_out = min(max_mobilize * 0.5, self.current_glycogen)
        fat_out = min(max_mobilize * 0.5, self.current_fat)
        self.current_glycogen -= glycogen_out
        self.current_fat -= fat_out
        return {
            "mobilized": {"glycogen": glycogen_out, "fat": fat_out},
            "remaining": {"glycogen": self.current_glycogen, "fat": self.current_fat},
        }

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        signal_strength = float(inputs.get("signal_strength", 0.5))
        duration_hr = float(inputs.get("duration_hr", 1.0))
        storage_inputs = inputs.get("storage_inputs")
        if isinstance(storage_inputs, dict):
            self.store({k: float(v) for k, v in storage_inputs.items()})
        return self.mobilize(signal_strength, duration_hr)
