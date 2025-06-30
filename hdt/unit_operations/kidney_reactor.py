"""Simulates renal filtration and urine production."""

from typing import Any, Dict

from .base_unit import BaseUnit


class KidneyReactor(BaseUnit):
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Simulates renal filtration and excretion of urea, water, and electrolytes.

        Args:
            config (dict): {
                - urea_clearance (mL/min)
                - fluid_reabsorption (0–1)
            }
        """
        self.urea_clearance = config.get("urea_clearance", 55)  # mL/min
        self.fluid_reabsorption = config.get("fluid_reabsorption", 0.96)

    def reset(self) -> None:
        """No internal state to reset for now."""

    def get_state(self) -> Dict[str, Any]:
        return {}

    def set_state(self, state_dict: Dict[str, Any]) -> None:
        """This unit maintains no persistent state."""

    def filter(
        self, blood_input: Dict[str, float], duration_min: int = 60
    ) -> Dict[str, Dict[str, float]]:
        """
        Filters blood for urea and water removal.

        Args:
            blood_input (dict): {
                'urea': mmol,
                'water': mL
            }
            duration_min (int): Duration in minutes

        Returns:
            dict: {
                'urine_output': {
                    'urea': mmol,
                    'water': mL
                },
                'retained': {
                    'urea': mmol,
                    'water': mL
                }
            }
        """
        # Urea output
        urea_out = min(
            blood_input.get("urea", 0), self.urea_clearance * duration_min / 1000
        )  # mmol

        # Water output
        total_water = blood_input.get("water", 0)
        water_out = total_water * (1 - self.fluid_reabsorption)

        # Retained
        retained_water = total_water - water_out
        retained_urea = blood_input.get("urea", 0) - urea_out

        return {
            "urine_output": {"urea": urea_out, "water": water_out},
            "retained": {"urea": retained_urea, "water": retained_water},
        }

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Wrapper for :meth:`filter` using dict input."""
        blood_input = inputs.get("blood_input", {})
        if not isinstance(blood_input, dict):
            blood_input = {}
        duration_min = int(inputs.get("duration_min", 60))
        return self.filter(blood_input, duration_min)
