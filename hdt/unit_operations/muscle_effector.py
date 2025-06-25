
class MuscleEffector:
    def __init__(self, config):
        """
        Simulates energy usage in muscle based on physical activity and hormone influence.

        Args:
            config (dict): {
                - resting_atp_demand (mmol/min)
                - exercise_factor (multiplier of ATP use)
                - fat_utilization_rate (g/hr at rest)
            }
        """
        self.resting_atp_demand = config.get("resting_atp_demand", 2.5)
        self.exercise_factor = config.get("exercise_factor", 4.0)
        self.fat_utilization_rate = config.get("fat_utilization_rate", 0.5)

    def metabolize(self, inputs, activity_level="rest", duration_min=60, hormones=None):
        """
        Simulates substrate metabolism during muscle activity.

        Args:
            inputs (dict): {
                - glucose (g)
                - fat (g)
                - ketones (optional, g)
            }
            activity_level (str): 'rest', 'moderate', 'high'
            duration_min (int): Duration of effort
            hormones (dict): {
                - insulin (0–1)
                - cortisol (0–1)
            }

        Returns:
            dict: {
                'substrate_used': {...},
                'exhaust': {co2, h2o},
                'to_brain': {fatigue_signal, lactate},
            }
        """
        factor = {
            "rest": 1.0,
            "moderate": 2.5,
            "high": self.exercise_factor
        }.get(activity_level, 1.0)

        insulin = hormones.get("insulin", 0.6) if hormones else 0.6
        cortisol = hormones.get("cortisol", 0.2) if hormones else 0.2

        atp_demand = self.resting_atp_demand * factor * duration_min

        # Hormonal impact
        insulin_sensitivity = 1.0 + (insulin - 0.5) * 0.4
        cortisol_penalty = 1.0 + cortisol * 0.3

        # Adjusted substrate usage
        glucose_use = min(inputs.get("glucose", 0), atp_demand * 0.5 / 10 * insulin_sensitivity / cortisol_penalty)
        fat_use = min(inputs.get("fat", 0), atp_demand * 0.3 / 9 / cortisol_penalty)
        ketone_use = min(inputs.get("ketones", 0), atp_demand * 0.2 / 8) if "ketones" in inputs else 0

        # Waste calculation
        co2_output = glucose_use * 0.8 + fat_use * 1.4 + ketone_use * 1.2
        h2o_output = glucose_use * 0.6 + fat_use * 1.1 + ketone_use * 1.0

        fatigue_signal = max(0, atp_demand - (glucose_use + fat_use + ketone_use) * 10)
        lactate = glucose_use * 0.1 if factor >= self.exercise_factor else 0

        return {
            "substrate_used": {
                "glucose": glucose_use,
                "fat": fat_use,
                "ketones": ketone_use
            },
            "exhaust": {
                "co2": co2_output,
                "h2o": h2o_output
            },
            "to_brain": {
                "fatigue_signal": fatigue_signal,
                "lactate": lactate
            }
        }
