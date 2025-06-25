
class LiverMetabolicRouter:
    def __init__(self, config):
        """
        Liver router that handles nutrient processing, storage, and mobilization.
        Supports 6 major stream interfaces including gut, colon, storage, and muscle.

        Args:
            config (dict): Configuration values:
                - glycogen_capacity (g)
                - gluconeogenesis_rate (g/hr)
                - insulin_sensitivity (0–1)
                - glucagon_sensitivity (0–1)
        """
        self.glycogen_capacity = config.get("glycogen_capacity", 100.0)
        self.gluconeogenesis_rate = config.get("gluconeogenesis_rate", 1.0)
        self.insulin_sensitivity = config.get("insulin_sensitivity", 0.7)
        self.glucagon_sensitivity = config.get("glucagon_sensitivity", 0.7)

        self.current_glycogen = 0.0

    def route(
        self,
        portal_input,
        microbiome_input=None,
        mobilized_reserves=None,
        signals=None
    ):
        """
        Routes portal nutrients, gut signals, and storage reserves.

        Args:
            portal_input (dict): From Gut via Cardiovascular system:
                - glucose, fatty_acids, amino_acids, water
            microbiome_input (dict): SCFAs, e.g., {"acetate": g, "butyrate": g}
            mobilized_reserves (dict): From storage unit
                - glycogen, fat
            signals (dict): Control hormones, e.g.:
                - insulin, glucagon

        Returns:
            dict: {
                'to_storage': {...},
                'to_muscle_aerobic': {...},
                'to_muscle_anaerobic': {...},
                'signals_to_brain': {...}
            }
        """
        signals = signals or {"insulin": 0.5, "glucagon": 0.5}
        microbiome_input = microbiome_input or {}
        mobilized_reserves = mobilized_reserves or {}

        insulin = signals["insulin"] * self.insulin_sensitivity
        glucagon = signals["glucagon"] * self.glucagon_sensitivity

        # Glycogen storage logic
        glycogen_room = self.glycogen_capacity - self.current_glycogen
        glycogen_stored = min(portal_input["glucose"] * insulin, glycogen_room)
        self.current_glycogen += glycogen_stored
        glucose_remaining = portal_input["glucose"] - glycogen_stored

        # Fat partitioning
        fat_stored = portal_input["fatty_acids"] * insulin
        fat_to_muscle = portal_input["fatty_acids"] - fat_stored

        # Amino acid use → gluconeogenesis
        new_glucose = min(self.gluconeogenesis_rate, portal_input["amino_acids"])
        glucose_remaining += new_glucose

        # Mobilized reserves
        glycogen_released = mobilized_reserves.get("glycogen", 0) * glucagon * 0.5
        fat_released = mobilized_reserves.get("fat", 0) * glucagon * 0.5

        # Update state
        self.current_glycogen = max(0.0, self.current_glycogen - glycogen_released)

        # Anaerobic logic (e.g. ketones if glucagon high)
        ketones = fat_released * 0.2 if glucagon > 0.5 else 0.0

        return {
            "to_storage": {
                "glycogen_stored": glycogen_stored,
                "fat_stored": fat_stored
            },
            "to_muscle_aerobic": {
                "glucose": glucose_remaining + glycogen_released,
                "fat": fat_to_muscle + fat_released
            },
            "to_muscle_anaerobic": {
                "glucose": glucose_remaining * 0.3,
                "ketones": ketones
            },
            "signals_to_brain": {
                "scfas": microbiome_input,
                "glucose_availability": glucose_remaining,
                "glycogen_level": self.current_glycogen
            }
        }
