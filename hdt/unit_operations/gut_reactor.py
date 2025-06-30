from typing import Any, Dict, Optional

from .base_unit import BaseUnit


class GutReactor(BaseUnit):
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Simulates gastrointestinal processing of ingested food using ODEs or static digestion.

        Args:
            config (dict): {
                - digestion_efficiency (0–1)
                - gastric_emptying_rate (g/min)
                - absorption_delay (min)
            }
        """
        self.digestion_efficiency = config.get("digestion_efficiency", 0.9)
        self.gastric_emptying_rate = config.get("gastric_emptying_rate", 1.5)  # g/min
        self.absorption_delay = config.get("absorption_delay", 10)  # not used yet

        # Internal state variables for ODE simulation
        self.glucose = 0.0
        self.fatty_acids = 0.0
        self.amino_acids = 0.0
        self.water = 0.0

        # Optional override for real-time control via the simulator
        self.override_inputs: Optional[Dict[str, Any]] = None

    def reset(self) -> None:
        """Reset internal nutrient pools."""
        self.glucose = 0.0
        self.fatty_acids = 0.0
        self.amino_acids = 0.0
        self.water = 0.0

    def load_meal(
        self,
        meal_input: Dict[str, float],
        hormones: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Loads a meal into the gut for continuous simulation.
        """
        circadian_tone = hormones.get("circadian_tone", 1.0) if hormones else 1.0
        cortisol = hormones.get("cortisol", 0.0) if hormones else 0.0
        efficiency_modifier = circadian_tone * (1.0 - 0.3 * cortisol)
        digestion_eff = self.digestion_efficiency * efficiency_modifier

        self.glucose = meal_input.get("carbs", 0.0) * digestion_eff
        self.fatty_acids = meal_input.get("fat", 0.0) * digestion_eff
        self.amino_acids = meal_input.get("protein", 0.0) * digestion_eff
        self.water = meal_input.get("water", 0.0) * digestion_eff
        # Fiber remains residue — not modeled here

    def get_state(self) -> Dict[str, float]:
        return {
            "gut_glucose": self.glucose,
            "gut_fatty_acids": self.fatty_acids,
            "gut_amino_acids": self.amino_acids,
            "gut_water": self.water,
        }

    def set_state(self, state_dict: Dict[str, float]) -> None:
        self.glucose = state_dict["gut_glucose"]
        self.fatty_acids = state_dict["gut_fatty_acids"]
        self.amino_acids = state_dict["gut_amino_acids"]
        self.water = state_dict["gut_water"]

    def inject_override(self, inputs: Dict[str, Any]) -> None:
        """Store override inputs to be used on the next :meth:`step` call."""
        self.override_inputs = inputs

    def derivatives(self, t: float, state: Dict[str, float]) -> Dict[str, float]:
        """
        Simulates continuous absorption using first-order kinetics.
        dX/dt = -k * X
        """
        k = self.gastric_emptying_rate / 100  # Normalize rate (can tune later)

        return {
            "gut_glucose": -k * state["gut_glucose"],
            "gut_fatty_acids": -k * state["gut_fatty_acids"],
            "gut_amino_acids": -k * state["gut_amino_acids"],
            "gut_water": -k * state["gut_water"],
        }

    def digest(
        self,
        meal_input: Dict[str, float],
        duration_min: int = 60,
        hormones: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Static digestion for backward compatibility or simple use.
        """
        circadian_tone = hormones.get("circadian_tone", 1.0) if hormones else 1.0
        cortisol = hormones.get("cortisol", 0.0) if hormones else 0.0

        efficiency_modifier = circadian_tone * (1.0 - 0.3 * cortisol)
        digestion_eff = self.digestion_efficiency * efficiency_modifier
        max_digestion = self.gastric_emptying_rate * duration_min

        absorbed = {
            "glucose": 0.0,
            "fatty_acids": 0.0,
            "amino_acids": 0.0,
            "water": 0.0,
        }
        residue = {}

        for nutrient, total in meal_input.items():
            if nutrient == "fiber":
                residue[nutrient] = total
                continue

            to_digest = min(total, max_digestion)
            absorbed_amt = to_digest * digestion_eff
            residue_amt = total - absorbed_amt

            if nutrient == "carbs":
                absorbed["glucose"] = round(absorbed_amt, 2)
            elif nutrient == "fat":
                absorbed["fatty_acids"] = round(absorbed_amt, 2)
            elif nutrient == "protein":
                absorbed["amino_acids"] = round(absorbed_amt, 2)
            elif nutrient == "water":
                absorbed["water"] = round(absorbed_amt, 2)

            residue[nutrient] = round(residue_amt, 2)

        return {"absorbed": absorbed, "residue": residue}

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        meal_input = inputs.get("meal_input", {})
        if not isinstance(meal_input, dict):
            meal_input = {}
        duration_min = int(inputs.get("duration_min", 60))
        hormones = inputs.get("hormones")
        if self.override_inputs is not None:
            o = self.override_inputs
            meal_input = o.get("meal_input", meal_input)
            duration_min = o.get("duration_min", duration_min)
            hormones = o.get("hormones", hormones)
            self.override_inputs = None

        return self.digest(meal_input, duration_min, hormones)
