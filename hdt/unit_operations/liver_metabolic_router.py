from typing import Any, Dict, Optional

from .base_unit import BaseUnit


class LiverMetabolicRouter(BaseUnit):
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Liver router that handles nutrient processing, storage, and mobilization.

        Args:
            config (dict): {
                - glycogen_capacity (g)
                - gluconeogenesis_rate (g/hr)
                - insulin_sensitivity (0–1)
                - glucagon_sensitivity (0–1)
            }
        """
        self.glycogen_capacity = config.get("glycogen_capacity", 100.0)
        self.gluconeogenesis_rate = config.get("gluconeogenesis_rate", 1.0)
        self.insulin_sensitivity = config.get("insulin_sensitivity", 0.7)
        self.glucagon_sensitivity = config.get("glucagon_sensitivity", 0.7)

        # Internal state for ODE
        self.liver_glucose = 0.0
        self.current_glycogen = 0.0

        # External inputs for derivative logic
        self._incoming_glucose = 0.0
        self._insulin = 0.5
        self._glucagon = 0.5

        # Optional override for real-time control
        self.override_inputs: Optional[Dict[str, Any]] = None

    def reset(self) -> None:
        """Reset internal liver state."""
        self.liver_glucose = 0.0
        self.current_glycogen = 0.0
        self._incoming_glucose = 0.0
        self._insulin = 0.5
        self._glucagon = 0.5

    def load_portal_input(
        self, portal_input: Dict[str, float], signals: Optional[Dict[str, float]] = None
    ) -> None:
        """
        Used for continuous simulation: sets incoming glucose & hormone levels.
        """
        self._incoming_glucose = portal_input.get("glucose", 0.0)
        signals = signals or {}
        self._insulin = signals.get("insulin", 0.5)
        self._glucagon = signals.get("glucagon", 0.5)

    def get_state(self) -> Dict[str, float]:
        return {
            "liver_glucose": self.liver_glucose,
            "liver_glycogen": self.current_glycogen,
        }

    def set_state(self, state_dict: Dict[str, float]) -> None:
        self.liver_glucose = state_dict["liver_glucose"]
        self.current_glycogen = state_dict["liver_glycogen"]

    def inject_override(self, inputs: Dict[str, Any]) -> None:
        """Store override inputs to be used on the next :meth:`step` call."""
        self.override_inputs = inputs

    def derivatives(self, t: float, state: Dict[str, float]) -> Dict[str, float]:
        """
        ODE model: glucose from gut is stored as glycogen based on insulin levels.
        """
        glucose = state["liver_glucose"]
        glycogen = state["liver_glycogen"]
        glycogen_room = self.glycogen_capacity - glycogen

        insulin_effect = self._insulin * self.insulin_sensitivity
        glucagon_effect = self._glucagon * self.glucagon_sensitivity

        # Glucose storage rate (proportional to insulin)
        glycogen_storage_rate = min(glucose * insulin_effect, glycogen_room)
        # Glycogen mobilization (proportional to glucagon)
        glycogen_release_rate = glycogen * glucagon_effect * 0.05  # slow breakdown

        d_glucose_dt = (
            self._incoming_glucose - glycogen_storage_rate + glycogen_release_rate
        )
        d_glycogen_dt = glycogen_storage_rate - glycogen_release_rate

        return {"liver_glucose": d_glucose_dt, "liver_glycogen": d_glycogen_dt}

    def route(
        self,
        portal_input: Dict[str, float],
        microbiome_input: Optional[Dict[str, float]] = None,
        mobilized_reserves: Optional[Dict[str, float]] = None,
        signals: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Static / discrete logic version of liver routing.
        """
        signals = signals or {"insulin": 0.5, "glucagon": 0.5}
        microbiome_input = microbiome_input or {}
        mobilized_reserves = mobilized_reserves or {}

        insulin = signals["insulin"] * self.insulin_sensitivity
        glucagon = signals["glucagon"] * self.glucagon_sensitivity

        glycogen_room = self.glycogen_capacity - self.current_glycogen
        glycogen_stored = min(portal_input["glucose"] * insulin, glycogen_room)
        self.current_glycogen += glycogen_stored
        glucose_remaining = portal_input["glucose"] - glycogen_stored

        fat_stored = portal_input["fatty_acids"] * insulin
        fat_to_muscle = portal_input["fatty_acids"] - fat_stored

        new_glucose = min(self.gluconeogenesis_rate, portal_input["amino_acids"])
        glucose_remaining += new_glucose

        glycogen_released = mobilized_reserves.get("glycogen", 0) * glucagon * 0.5
        fat_released = mobilized_reserves.get("fat", 0) * glucagon * 0.5
        self.current_glycogen = max(0.0, self.current_glycogen - glycogen_released)

        ketones = fat_released * 0.2 if glucagon > 0.5 else 0.0

        return {
            "to_storage": {
                "glycogen_stored": glycogen_stored,
                "fat_stored": fat_stored,
            },
            "to_muscle_aerobic": {
                "glucose": glucose_remaining + glycogen_released,
                "fat": fat_to_muscle + fat_released,
            },
            "to_muscle_anaerobic": {
                "glucose": glucose_remaining * 0.3,
                "ketones": ketones,
            },
            "signals_to_brain": {
                "scfas": microbiome_input,
                "glucose_availability": glucose_remaining,
                "glycogen_level": self.current_glycogen,
            },
        }

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        portal_input = inputs.get("portal_input", {})
        if not isinstance(portal_input, dict):
            portal_input = {}
        microbiome_input = inputs.get("microbiome_input")
        mobilized_reserves = inputs.get("mobilized_reserves")
        signals = inputs.get("signals")
        if self.override_inputs is not None:
            o = self.override_inputs
            portal_input = o.get("portal_input", portal_input)
            microbiome_input = o.get("microbiome_input", microbiome_input)
            mobilized_reserves = o.get("mobilized_reserves", mobilized_reserves)
            signals = o.get("signals", signals)
            self.override_inputs = None

        return self.route(portal_input, microbiome_input, mobilized_reserves, signals)
