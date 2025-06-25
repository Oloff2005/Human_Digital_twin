
class StorageUnit:
    def __init__(self, config):
        """
        Manages energy reserve storage (glycogen, fat) and mobilization.

        Args:
            config (dict): {
                - max_glycogen (g)
                - max_fat (g)
                - mobilization_rate (g/hr)
            }
        """
        self.max_glycogen = config.get("max_glycogen", 400)
        self.max_fat = config.get("max_fat", 12000)
        self.mobilization_rate = config.get("mobilization_rate", 60)  # g/hr

        # Internal state
        self.current_glycogen = config.get("initial_glycogen", 300)
        self.current_fat = config.get("initial_fat", 8000)

    def store(self, inputs):
        """
        Stores excess energy.

        Args:
            inputs (dict): {
                - glycogen_stored: g
                - fat_stored: g
            }

        Returns:
            dict: updated_state
        """
        self.current_glycogen = min(self.max_glycogen, self.current_glycogen + inputs.get("glycogen_stored", 0))
        self.current_fat = min(self.max_fat, self.current_fat + inputs.get("fat_stored", 0))

        return {
            "glycogen": self.current_glycogen,
            "fat": self.current_fat
        }

    def mobilize(self, signal_strength=0.5, duration_hr=1.0):
        """
        Releases stored energy based on glucagon-like signal.

        Args:
            signal_strength (float): 0–1, proportional to glucagon
            duration_hr (float): time under fasting/mobilization

        Returns:
            dict: {
                'mobilized': {
                    'glycogen': g,
                    'fat': g
                },
                'remaining': {
                    'glycogen': g,
                    'fat': g
                }
            }
        """
        max_mobilize = self.mobilization_rate * duration_hr * signal_strength

        glycogen_out = min(max_mobilize * 0.5, self.current_glycogen)
        fat_out = min(max_mobilize * 0.5, self.current_fat)

        self.current_glycogen -= glycogen_out
        self.current_fat -= fat_out

        return {
            "mobilized": {
                "glycogen": glycogen_out,
                "fat": fat_out
            },
            "remaining": {
                "glycogen": self.current_glycogen,
                "fat": self.current_fat
            }
        }
