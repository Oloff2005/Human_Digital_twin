from .base_unit import BaseUnit


class LungReactor(BaseUnit):
    def __init__(self, config=None, oxygen_uptake_rate=320, co2_exhale_rate=250):
        """Simulate lung gas exchange for oxygen uptake and CO₂ removal.

        Parameters
        ----------
        config : dict, optional
            Optional configuration dictionary so this unit matches the pattern of
            other unit operations.
        oxygen_uptake_rate : float, optional
            Amount of oxygen delivered to the blood per minute (mL/min).
        co2_exhale_rate : float, optional
            Maximum amount of CO₂ that can be exhaled per minute (mL/min).
        """
        if isinstance(config, dict):
            oxygen_uptake_rate = config.get("oxygen_uptake_rate", oxygen_uptake_rate)
            co2_exhale_rate = config.get("co2_exhale_rate", co2_exhale_rate)

        self.oxygen_uptake_rate = oxygen_uptake_rate
        self.co2_exhale_rate = co2_exhale_rate

        # Internal state used by the ODE solver
        self.co2_pool = 0.0
        self._co2_in_rate = 0.0  # rate of CO₂ coming from tissues (mL/min)

    # Optional override for real-time control
        self.override_inputs = None

    def reset(self):
        """Reset accumulated CO₂ pool."""
        self.co2_pool = 0.0
        self._co2_in_rate = 0.0

    def exchange(self, duration_min=1, co2_in=0):
        """Perform discrete gas exchange for a given time step."""

        self.co2_pool += co2_in

        oxygen_delivered = self.oxygen_uptake_rate * duration_min
        exhale_capacity = self.co2_exhale_rate * duration_min

        co2_exhaled = min(exhale_capacity, self.co2_pool)
        self.co2_pool -= co2_exhaled

        return {
            "oxygen_to_blood": oxygen_delivered,
            "co2_exhaled": co2_exhaled,
            "co2_remaining": self.co2_pool,
        }

    def step(self, duration_min=1, co2_in=0):
        """
        Execute one simulation step for the lungs.

        Returns:
            dict: Gas exchange outputs
        """
        if self.override_inputs is not None:
            o = self.override_inputs
            duration_min = o.get("duration_min", duration_min)
            co2_in = o.get("co2_in", co2_in)
            self.override_inputs = None

        return self.exchange(duration_min, co2_in)

    # ------------------------------------------------------------------
    # ODE compatibility methods
    def get_state(self):
        return {"lung_co2": self.co2_pool}

    def set_state(self, state_dict):
        self.co2_pool = state_dict["lung_co2"]

    def inject_override(self, inputs: dict):
        """Store override inputs to be used on the next :meth:`step` call."""
        self.override_inputs = inputs

    def derivatives(self, t, state):
        """Rate of change of CO₂ in the lung pool."""
        co2_pool = state["lung_co2"]
        exhale = min(self.co2_exhale_rate, co2_pool)
        d_co2_dt = self._co2_in_rate - exhale
        return {"lung_co2": d_co2_dt}
