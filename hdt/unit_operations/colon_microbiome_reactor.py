from typing import Any, Dict

from .base_unit import BaseUnit


class ColonMicrobiomeReactor(BaseUnit):
    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Simulates fiber fermentation, short-chain fatty acid (SCFA) production,
        and gut-brain signaling via microbiome.

        Args:
            config (dict): {
                - fiber_fermentation_efficiency: 0–1
                - scfa_profile: dict with ratios of acetate, propionate, butyrate
                - transit_time: min until waste exits
            }
        """
        self.efficiency = config.get("fiber_fermentation_efficiency", 0.5)
        self.scfa_profile = config.get(
            "scfa_profile", {"acetate": 0.6, "propionate": 0.2, "butyrate": 0.2}
        )
        self.transit_time = config.get("transit_time", 480)  # 8 hours

    def reset(self) -> None:
        """No persistent state to reset."""
        pass

    def get_state(self) -> Dict[str, Any]:
        return {}

    def set_state(self, state_dict: Dict[str, Any]) -> None:
        pass

    def process_residue(self, fiber_input: float) -> Dict[str, Any]:
        """
        Ferments unabsorbed fiber to produce SCFAs and waste.

        Args:
            fiber_input (float): grams of fiber from GutReactor

        Returns:
            dict: {
                'scfa_output': {acetate, propionate, butyrate},
                'fecal_waste': float (g),
                'gut_brain_signals': dict
            }
        """
        scfa_total = fiber_input * self.efficiency
        fecal_waste = fiber_input - scfa_total

        scfa_output = {k: scfa_total * v for k, v in self.scfa_profile.items()}

        gut_signals = {
            "total_scfa": scfa_total,
            "butyrate_signal": scfa_output.get("butyrate", 0),
            "fermentation_ratio": self.efficiency,
            "waste_transit_time": self.transit_time,
        }

        return {
            "scfa_output": scfa_output,
            "fecal_waste": fecal_waste,
            "gut_brain_signals": gut_signals,
        }

    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper for :meth:`process_residue` using dict input."""
        fiber_input = float(inputs.get("fiber_input", 0.0))
        return self.process_residue(fiber_input)
