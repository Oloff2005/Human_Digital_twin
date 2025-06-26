class PancreaticValve:
    def __init__(self, config):
        """
        Simulates insulin/glucagon release in response to blood glucose.

        Args:
            config (dict): {
                - insulin_release_threshold (float, mmol/L)
                - glucagon_release_threshold (float, mmol/L)
            }
        """
        self.insulin_threshold = config.get("insulin_release_threshold", 5.2)
        self.glucagon_threshold = config.get("glucagon_release_threshold", 4.2)

    def regulate(self, blood_glucose_mmol_per_L, rate_of_change=0.0):
        """
        Releases insulin or glucagon based on glucose level and change.

        Args:
            blood_glucose_mmol_per_L (float): Current glucose level (mmol/L)
            rate_of_change (float): Slope of glucose change (mmol/L/hr)

        Returns:
            dict: {
                'insulin': 0–1,
                'glucagon': 0–1
            }
        """
        insulin = 0.0
        glucagon = 0.0

        if blood_glucose_mmol_per_L >= self.insulin_threshold:
            insulin = min(1.0, 0.5 + (blood_glucose_mmol_per_L - self.insulin_threshold) * 0.2)
        elif blood_glucose_mmol_per_L <= self.glucagon_threshold:
            glucagon = min(1.0, 0.5 + (self.glucagon_threshold - blood_glucose_mmol_per_L) * 0.3)

        # Slight adjustment based on trend
        insulin = max(0.0, min(1.0, insulin + rate_of_change * 0.1))
        glucagon = max(0.0, min(1.0, glucagon - rate_of_change * 0.1))

        return {
            "insulin": round(insulin, 3),
            "glucagon": round(glucagon, 3)
        }

    def step(self, glucose, rate_of_change=0.0):
        """
        Executes one simulation step for hormone regulation.

        Args:
            glucose (float): Current blood glucose level (mmol/L)
            rate_of_change (float): Glucose trend (optional)

        Returns:
            dict: {'insulin': x, 'glucagon': y}
        """
        return self.regulate(glucose, rate_of_change)
