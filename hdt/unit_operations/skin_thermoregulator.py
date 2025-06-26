class SkinThermoregulator:
    def __init__(self, config):
        """
        Simulates temperature regulation via sweating and vasodilation.

        Args:
            config (dict): {
                - sweat_rate_max (L/hr)
                - vasodilation_temp_threshold (°C)
            }
        """
        self.sweat_rate_max = config.get("sweat_rate_max", 1.8)
        self.vasodilation_temp_threshold = config.get("vasodilation_temp_threshold", 37.2)

    def regulate(self, core_temp, ambient_temp, duration_hr=1.0, hormones=None):
        """
        Regulates body heat via sweating and skin blood flow.

        Args:
            core_temp (float): Core body temperature in °C
            ambient_temp (float): Environmental temperature in °C
            duration_hr (float): Duration in hours
            hormones (dict): {
                - cortisol (0–1) (optional): stress affects sweating
            }

        Returns:
            dict: {
                'sweat_loss': L,
                'vasodilation': bool,
                'heat_stress_score': 0–1
            }
        """
        cortisol = hormones.get("cortisol", 0.0) if hormones else 0.0

        # Vasodilation logic
        vasodilation = core_temp >= self.vasodilation_temp_threshold

        # Sweating logic: increase with temp, decrease under stress
        temp_diff = max(0, core_temp - self.vasodilation_temp_threshold)
        sweat_rate = min(self.sweat_rate_max, temp_diff * 1.2)  # L/hr

        # Cortisol (stress) reduces sweat output
        sweat_rate *= (1.0 - 0.3 * cortisol)

        sweat_loss = sweat_rate * duration_hr

        # Heat stress score (0–1)
        stress_score = min(1.0, temp_diff / 3.0 + 0.2 * cortisol)

        return {
            "sweat_loss": round(sweat_loss, 2),
            "vasodilation": vasodilation,
            "heat_stress_score": round(stress_score, 2)
        }

    def step(self, core_temp, ambient_temp, duration_hr=1.0, hormones=None):
        """
        Executes one simulation step for thermoregulation.

        Returns:
            dict: Thermoregulatory response
        """
        return self.regulate(core_temp, ambient_temp, duration_hr, hormones)
