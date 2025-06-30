from typing import Any, Dict, Optional

from .base_unit import BaseUnit


class MuscleEffector(BaseUnit):
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Simulates energy usage in muscle based on physical activity and hormone influence.
        """
        self.resting_atp_demand = config.get("resting_atp_demand", 2.5)
        self.exercise_factor = config.get("exercise_factor", 4.0)
        self.fat_utilization_rate = config.get("fat_utilization_rate", 0.5)

        self.glucose = 0.0
        self.fat = 0.0
        self.ketones = 0.0

        self.activity_level = "rest"
        self.hormones = {"insulin": 0.6, "cortisol": 0.2}

        # Optional override for simulator injections
        self.override_inputs = None

    def reset(self) -> None:
        """Reset internal substrate pools and settings."""
        self.glucose = 0.0
        self.fat = 0.0
        self.ketones = 0.0
        self.activity_level = "rest"
        self.hormones = {"insulin": 0.6, "cortisol": 0.2}

    def load_inputs(
        self,
        substrate_pool: Dict[str, float],
        activity_level: str = "rest",
        hormones: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Sets internal fuel stores (glucose, fat, ketones) and external influences.
        """
        self.glucose = substrate_pool.get("glucose", 0.0)
        self.fat = substrate_pool.get("fat", 0.0)
        self.ketones = substrate_pool.get("ketones", 0.0)
        self.activity_level = activity_level
        self.hormones = hormones or {"insulin": 0.6, "cortisol": 0.2}

    def get_state(self) -> Dict[str, float]:
        return {
            "muscle_glucose": self.glucose,
            "muscle_fat": self.fat,
            "muscle_ketones": self.ketones,
        }

    def set_state(self, state_dict: Dict[str, float]) -> None:
        self.glucose = state_dict["muscle_glucose"]
        self.fat = state_dict["muscle_fat"]
        self.ketones = state_dict["muscle_ketones"]

    def inject_override(self, inputs: Dict[str, Any]) -> None:
        """Store override inputs to be used on the next :meth:`step` call."""
        self.override_inputs = inputs

    def derivatives(self, t: float, state: Dict[str, float]) -> Dict[str, float]:
        """
        Calculates substrate usage rates based on current state and hormones.
        """
        factor = {"rest": 1.0, "moderate": 2.5, "high": self.exercise_factor}.get(
            self.activity_level, 1.0
        )

        insulin = self.hormones.get("insulin", 0.6)
        cortisol = self.hormones.get("cortisol", 0.2)

        atp_demand = self.resting_atp_demand * factor * 1  # assuming 1-hour timestep
        insulin_sensitivity = 1.0 + (insulin - 0.5) * 0.4
        cortisol_penalty = 1.0 + cortisol * 0.3

        glucose_use = min(
            state["muscle_glucose"],
            atp_demand * 0.5 / 10 * insulin_sensitivity / cortisol_penalty,
        )
        fat_use = min(state["muscle_fat"], atp_demand * 0.3 / 9 / cortisol_penalty)
        ketone_use = min(state["muscle_ketones"], atp_demand * 0.2 / 8)

        return {
            "muscle_glucose": -glucose_use,
            "muscle_fat": -fat_use,
            "muscle_ketones": -ketone_use,
        }

    def step(
        self,
        inputs: Dict[str, float],
        activity_level: str = "rest",
        duration_min: int = 60,
        hormones: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        if self.override_inputs is not None:
            o = self.override_inputs
            inputs = o.get("inputs", inputs)
            activity_level = o.get("activity_level", activity_level)
            duration_min = o.get("duration_min", duration_min)
            hormones = o.get("hormones", hormones)
            self.override_inputs = None

        return self.metabolize(inputs, activity_level, duration_min, hormones)

    def metabolize(
        self,
        inputs: Dict[str, float],
        activity_level: str = "rest",
        duration_min: int = 60,
        hormones: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Optional discrete simulation mode (unchanged).
        """
        factor = {"rest": 1.0, "moderate": 2.5, "high": self.exercise_factor}.get(
            activity_level, 1.0
        )

        insulin = hormones.get("insulin", 0.6) if hormones else 0.6
        cortisol = hormones.get("cortisol", 0.2) if hormones else 0.2

        atp_demand = self.resting_atp_demand * factor * duration_min

        insulin_sensitivity = 1.0 + (insulin - 0.5) * 0.4
        cortisol_penalty = 1.0 + cortisol * 0.3

        glucose_use = min(
            inputs.get("glucose", 0),
            atp_demand * 0.5 / 10 * insulin_sensitivity / cortisol_penalty,
        )
        fat_use = min(inputs.get("fat", 0), atp_demand * 0.3 / 9 / cortisol_penalty)
        ketone_use = (
            min(inputs.get("ketones", 0), atp_demand * 0.2 / 8)
            if "ketones" in inputs
            else 0
        )

        co2_output = glucose_use * 0.8 + fat_use * 1.4 + ketone_use * 1.2
        h2o_output = glucose_use * 0.6 + fat_use * 1.1 + ketone_use * 1.0

        fatigue_signal = max(0, atp_demand - (glucose_use + fat_use + ketone_use) * 10)
        lactate = glucose_use * 0.1 if factor >= self.exercise_factor else 0

        return {
            "substrate_used": {
                "glucose": glucose_use,
                "fat": fat_use,
                "ketones": ketone_use,
            },
            "exhaust": {"co2": co2_output, "h2o": h2o_output},
            "to_brain": {"fatigue_signal": fatigue_signal, "lactate": lactate},
        }
