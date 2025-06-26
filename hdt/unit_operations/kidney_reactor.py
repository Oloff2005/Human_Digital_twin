class KidneyReactor:
    def __init__(self, config):
        """
        Simulates renal filtration and excretion of urea, water, and electrolytes.

        Args:
            config (dict): {
                - urea_clearance (mL/min)
                - fluid_reabsorption (0–1)
            }
        """
        self.urea_clearance = config.get("urea_clearance", 55)  # mL/min
        self.fluid_reabsorption = config.get("fluid_reabsorption", 0.96)

    def filter(self, blood_input, duration_min=60):
        """
        Filters blood for urea and water removal.

        Args:
            blood_input (dict): {
                'urea': mmol,
                'water': mL
            }
            duration_min (int): Duration in minutes

        Returns:
            dict: {
                'urine_output': {
                    'urea': mmol,
                    'water': mL
                },
                'retained': {
                    'urea': mmol,
                    'water': mL
                }
            }
        """
        # Urea output
        urea_out = min(blood_input.get("urea", 0), self.urea_clearance * duration_min / 1000)  # mmol

        # Water output
        total_water = blood_input.get("water", 0)
        water_out = total_water * (1 - self.fluid_reabsorption)

        # Retained
        retained_water = total_water - water_out
        retained_urea = blood_input.get("urea", 0) - urea_out

        return {
            "urine_output": {
                "urea": urea_out,
                "water": water_out
            },
            "retained": {
                "urea": retained_urea,
                "water": retained_water
            }
        }

    def step(self, blood_input, duration_min=60):
        """
        Wrapper to standardize simulation interface.

        Returns:
            dict: Output from renal processing
        """
        return self.filter(blood_input, duration_min)
