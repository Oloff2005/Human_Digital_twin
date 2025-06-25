
class CardiovascularTransport:
    def __init__(self, config):
        """
        Simulates transport of absorbed nutrients and hormones.

        Args:
            config (dict): Parameters for cardiovascular transport:
                - cardiac_output (float): L/min
                - hormone_transport_delay (float): minutes
        """
        self.cardiac_output = config.get("cardiac_output", 5.0)
        self.hormone_transport_delay = config.get("hormone_transport_delay", 1.0)

    def distribute(self, absorbed_nutrients):
        """
        Distributes absorbed nutrients from gut to the liver and peripheral tissues.

        Args:
            absorbed_nutrients (dict): Output of GutReactor
                - glucose (g)
                - fatty_acids (g)
                - amino_acids (g)
                - water (g)

        Returns:
            dict: {
                'to_liver': { ... },
                'to_systemic': { ... },
                'delay_minutes': float
            }
        """
        if not all(k in absorbed_nutrients for k in ("glucose", "fatty_acids", "amino_acids", "water")):
            raise ValueError("Missing required nutrients in absorbed input.")

        # Estimate split: 70% of absorbed nutrients go through portal vein to liver
        to_liver = {k: v * 0.7 for k, v in absorbed_nutrients.items()}
        to_systemic = {k: v * 0.3 for k, v in absorbed_nutrients.items()}

        return {
            "to_liver": to_liver,
            "to_systemic": to_systemic,
            "delay_minutes": self.hormone_transport_delay
        }
