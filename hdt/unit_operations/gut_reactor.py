
class GutReactor:
    def __init__(self, config):
        """
        Simulates gastrointestinal processing of ingested food.

        Args:
            config (dict): {
                - digestion_efficiency (0–1)
                - gastric_emptying_rate (g/min)
                - absorption_delay (min)
            }
        """
        self.digestion_efficiency = config.get("digestion_efficiency", 0.9)
        self.gastric_emptying_rate = config.get("gastric_emptying_rate", 1.5)
        self.absorption_delay = config.get("absorption_delay", 10)

    def digest(self, meal_input, duration_min=60, hormones=None):
        """
        Digests input meal based on efficiency, hormones, and circadian rhythm.

        Args:
            meal_input (dict): {
                'carbs': g,
                'fat': g,
                'protein': g,
                'fiber': g,
                'water': mL
            }
            duration_min (int): digestion time
            hormones (dict): {
                - circadian_tone (0–1),
                - cortisol (0–1)
            }

        Returns:
            dict: {
                'absorbed': {...},
                'residue': {...}
            }
        """
        circadian_tone = hormones.get("circadian_tone", 1.0) if hormones else 1.0
        cortisol = hormones.get("cortisol", 0.0) if hormones else 0.0

        # Adjust digestion rate based on circadian and stress
        efficiency_modifier = circadian_tone * (1.0 - 0.3 * cortisol)
        digestion_eff = self.digestion_efficiency * efficiency_modifier

        max_digestion = self.gastric_emptying_rate * duration_min

        absorbed = {}
        residue = {}

        for nutrient, total in meal_input.items():
            if nutrient == "fiber":
                residue[nutrient] = total
                continue

            to_digest = min(total, max_digestion)
            absorbed_amt = to_digest * digestion_eff
            residue_amt = total - absorbed_amt

            absorbed[nutrient] = round(absorbed_amt, 2)
            residue[nutrient] = round(residue_amt, 2)

        return {
            "absorbed": absorbed,
            "residue": residue
        }
