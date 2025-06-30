from .base_unit import BaseUnit


class HeartCirculation(BaseUnit):
    def __init__(self, config):
        """Cardiovascular transport of nutrients and hormones.

        Parameters
        ----------
        config : dict
            Expected keys::

                - ``cardiac_output`` (float) – L/min
                - ``hormone_transport_delay`` (float) – minutes delay before
                  nutrients reach target tissues
        """
        # Basic properties
        self.cardiac_output = config.get("cardiac_output", 5.0)
        self.transport_delay = config.get("hormone_transport_delay", 1.0)

        # State variables used for ODE based transport delay
        self.cv_glucose = 0.0
        self.cv_fatty_acids = 0.0
        self.cv_amino_acids = 0.0
        self.cv_water = 0.0

        # Latest absorbed inputs for derivative calculations
        self._absorbed = {
            "glucose": 0.0,
            "fatty_acids": 0.0,
            "amino_acids": 0.0,
            "water": 0.0,
        }

    def reset(self):
        """Reset nutrient pools and absorbed inputs."""
        self.cv_glucose = 0.0
        self.cv_fatty_acids = 0.0
        self.cv_amino_acids = 0.0
        self.cv_water = 0.0
        self._absorbed = {
            "glucose": 0.0,
            "fatty_acids": 0.0,
            "amino_acids": 0.0,
            "water": 0.0,
        }

    def distribute(self, absorbed_nutrients):
        """Route nutrients from gut to liver and systemic tissues.

        Parameters
        ----------
        absorbed_nutrients : dict
            Should contain ``glucose``, ``fatty_acids``, ``amino_acids`` and ``water``.

        Returns
        -------
        dict
            Dictionary with keys ``to_liver`` and ``to_systemic`` each mapping to
            nutrient dictionaries, along with ``delay_minutes``.
        """
        required = ("glucose", "fatty_acids", "amino_acids", "water")
        if not all(k in absorbed_nutrients for k in required):
            raise ValueError("Missing required nutrients in absorbed input.")

        # Store for derivative calculations
        self._absorbed = {k: float(absorbed_nutrients.get(k, 0.0)) for k in required}

        to_liver = {k: v * 0.7 for k, v in absorbed_nutrients.items()}
        to_systemic = {k: v * 0.3 for k, v in absorbed_nutrients.items()}

        return {
            "to_liver": to_liver,
            "to_systemic": to_systemic,
            "delay_minutes": self.transport_delay,
        }

    def step(self, absorbed_nutrients):
        """Wrapper for :meth:`distribute` for unit operation API."""
        return self.distribute(absorbed_nutrients)

    # ------------------------------------------------------------------
    # ODE integration helpers
    # ------------------------------------------------------------------
    def get_state(self):
        """Return the current amounts of nutrients in transit."""
        return {
            "cv_glucose": self.cv_glucose,
            "cv_fatty_acids": self.cv_fatty_acids,
            "cv_amino_acids": self.cv_amino_acids,
            "cv_water": self.cv_water,
        }

    def set_state(self, state_dict):
        """Set the internal state from ``state_dict``."""
        self.cv_glucose = state_dict["cv_glucose"]
        self.cv_fatty_acids = state_dict["cv_fatty_acids"]
        self.cv_amino_acids = state_dict["cv_amino_acids"]
        self.cv_water = state_dict["cv_water"]

    def derivatives(self, t, state):
        """First-order delay dynamics for nutrient transport."""
        return {
            "cv_glucose": self._absorbed.get("glucose", 0.0)
            - state["cv_glucose"] / self.transport_delay,
            "cv_fatty_acids": self._absorbed.get("fatty_acids", 0.0)
            - state["cv_fatty_acids"] / self.transport_delay,
            "cv_amino_acids": self._absorbed.get("amino_acids", 0.0)
            - state["cv_amino_acids"] / self.transport_delay,
            "cv_water": self._absorbed.get("water", 0.0)
            - state["cv_water"] / self.transport_delay,
        }
