class LungReactor:
    def __init__(self, config):
        """
        Simulates gas exchange in the lungs (O2 uptake and CO2 exhalation).

        Args:
            config (dict): {
                - oxygen_uptake_rate (mL/min)
                - co2_exhale_rate (mL/min)
            }
        """
        self.oxygen_uptake_rate = config.get("oxygen_uptake_rate", 320)
        self.co2_exhale_rate = config.get("co2_exhale_rate", 250)

    def exchange(self, duration_min=1, co2_in=0):
        """
        Models oxygen delivery and CO2 removal.

        Args:
            duration_min (int): Duration in minutes
            co2_in (float): CO2 from tissues (e.g. muscles), in mL

        Returns:
            dict: {
                'oxygen_to_blood': mL,
                'co2_exhaled': mL,
                'co2_remaining': mL
            }
        """
        oxygen_delivered = self.oxygen_uptake_rate * duration_min
        co2_removed = min(self.co2_exhale_rate * duration_min, co2_in)
        co2_remaining = max(0, co2_in - co2_removed)

        return {
            "oxygen_to_blood": oxygen_delivered,
            "co2_exhaled": co2_removed,
            "co2_remaining": co2_remaining
        }

    def step(self, duration_min=1, co2_in=0):
        """
        Execute one simulation step for the lungs.

        Returns:
            dict: Gas exchange outputs
        """
        return self.exchange(duration_min, co2_in)
