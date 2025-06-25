# hormone_router.py

class HormoneRouter:
    def __init__(self, dominance_rules=None):
        """
        Modulates hormone signals by enforcing dominance rules.

        Args:
            dominance_rules (dict): keys are dominant hormones,
                                    values are lists of suppressed hormones.
        """
        self.dominance_rules = dominance_rules or {
            'cortisol': ['insulin', 'digestive_signal'],
            'glucagon': ['insulin'],
        }

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
