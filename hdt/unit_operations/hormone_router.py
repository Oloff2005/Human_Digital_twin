from .base_unit import BaseUnit


class HormoneRouter(BaseUnit):
    def __init__(self, dominance_rules=None):
        """
        Modulates hormone signals by enforcing dominance rules.

        Args:
            dominance_rules (dict): keys are dominant hormones,
                                    values are lists of suppressed hormones.
        """
        self.dominance_rules = dominance_rules or {
           "cortisol": ["insulin", "digestive_signal", "melatonin"],
           "glucagon": ["insulin"],
        }
    def reset(self):
        """No dynamic state to reset."""
        pass

    def get_state(self):
        return {}

    def set_state(self, state_dict):
        pass

    def resolve(self, hormone_outputs):
        """
        Adjust hormone signals based on dominance suppression logic.

        Args:
            hormone_outputs (dict): raw hormonal signals

        Returns:
            dict: adjusted hormone values
        """
        adjusted = hormone_outputs.copy()

        for dominant, suppressed_list in self.dominance_rules.items():
            strength = adjusted.get(dominant, 0)
            for suppressed in suppressed_list:
                if suppressed in adjusted:
                    adjusted[suppressed] *= max(0.0, 1 - 0.5 * strength)

        return adjusted
    
        # ------------------------------------------------------------------
    # New routing interface
    def route(self, hormone_candidates):
        """Resolve dominance for a set of hormone candidates.

        Parameters
        ----------
        hormone_candidates : dict
            Dictionary of candidate hormone levels (0-1) such as
            ``{"insulin": x, "glucagon": y, "cortisol": z, "melatonin": m}``.

        Returns
        -------
        dict
            Final hormone mix after applying dominance rules.
        """
        adjusted = self.resolve(hormone_candidates)
        return {k: round(v, 3) for k, v in adjusted.items()}

    def step(self, hormone_outputs):
        """
        Step method to fit simulation loop.

        Args:
            hormone_outputs (dict): raw hormones from BrainController

        Returns:
            dict: adjusted hormones after resolving dominance
        """
        return self.route(hormone_outputs)
