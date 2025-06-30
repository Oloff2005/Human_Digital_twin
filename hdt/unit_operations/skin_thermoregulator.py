"""Models sweat-driven heat dissipation and dry heat loss."""

from typing import Any, Dict, Optional

from .base_unit import BaseUnit


class SkinThermoregulator(BaseUnit):
    """Simple model of skin thermoregulation.

    This class offers a lightweight representation of sweating and heat
    dissipation.  It exposes an ``ODE`` friendly interface while maintaining
    the old :py:meth:`regulate` method for backward compatibility with the
    existing simulator and tests.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the regulator with optional tuning parameters."""

        # Maximum achievable sweat rate in L/hr
        self.sweat_rate_max = config.get("sweat_rate_max", 1.8)

        # Core temperature at which vasodilation/sweating begins (°C)
        self.vasodilation_temp_threshold = config.get(
            "vasodilation_temp_threshold", 37.2
        )

        # Amount of heat removed per litre of sweat (kcal)
        self.heat_loss_per_l = config.get("heat_loss_per_l", 580.0)

        # Coefficient for dry heat loss (kcal/hr per °C difference)
        self.conduction_coeff = config.get("conduction_coeff", 10.0)

        # Cumulative state variables for ODE integration
        self.total_sweat = 0.0  # litres
        self.total_heat_loss = 0.0  # kcal

        # Inputs used by ``derivatives``
        self._core_temp = self.vasodilation_temp_threshold
        self._ambient_temp = 25.0
        self._cortisol = 0.0

        # Optional override for real-time control
        self.override_inputs: Optional[Dict[str, Any]] = None

    def reset(self) -> None:
        """Reset cumulative sweat and heat loss."""
        self.total_sweat = 0.0
        self.total_heat_loss = 0.0
        self._core_temp = self.vasodilation_temp_threshold
        self._ambient_temp = 25.0
        self._cortisol = 0.0

    # ------------------------------------------------------------------
    # Discrete helper used by the simulator
    def regulate(
        self,
        core_temp: float,
        ambient_temp: float,
        duration_hr: float = 1.0,
        hormones: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Backward compatible wrapper around :meth:`step`."""

        cortisol = hormones.get("cortisol", 0.0) if hormones else 0.0
        out = self.step(
            {
                "core_temp": core_temp,
                "ambient_temp": ambient_temp,
                "cortisol": cortisol,
                "duration_hr": duration_hr,
            }
        )

        temp_diff = max(0, core_temp - self.vasodilation_temp_threshold)
        vasodilation = core_temp >= self.vasodilation_temp_threshold
        stress_score = min(1.0, temp_diff / 3.0 + 0.2 * cortisol)

        return {
            "sweat_loss": round(out["sweat_rate"] * duration_hr, 2),
            "vasodilation": vasodilation,
            "heat_stress_score": round(stress_score, 2),
        }

    # ------------------------------------------------------------------
    def step(self, inputs: Dict[str, Any]) -> Dict[str, float]:
        core_temp = float(inputs.get("core_temp", self.vasodilation_temp_threshold))
        ambient_temp = float(inputs.get("ambient_temp", 25.0))
        cortisol = float(inputs.get("cortisol", 0.0))
        duration_hr = float(inputs.get("duration_hr", 1.0))
        """Execute a discrete thermoregulation step.

        Parameters
        ----------
        core_temp : float
            Current core body temperature (°C).
        ambient_temp : float
            Environmental temperature (°C).
        cortisol : float, optional
            Stress hormone level on a 0–1 scale.
        duration_hr : float, optional
            Duration of the step in hours.

        Returns
        -------
        dict
            ``{"sweat_rate": L/hr, "heat_dissipated": kcal}``
        """
        if self.override_inputs is not None:
            o = self.override_inputs
            core_temp = o.get("core_temp", core_temp)
            ambient_temp = o.get("ambient_temp", ambient_temp)
            cortisol = o.get("cortisol", cortisol)
            duration_hr = o.get("duration_hr", duration_hr)
            self.override_inputs = None

        # Store inputs for the derivative interface
        self._core_temp = core_temp
        self._ambient_temp = ambient_temp
        self._cortisol = cortisol

        # Sweating model
        temp_diff = max(0.0, core_temp - self.vasodilation_temp_threshold)
        sweat_rate = min(self.sweat_rate_max, temp_diff * 1.2)
        sweat_rate *= 1.0 - 0.3 * cortisol

        # Heat loss via sweat evaporation + dry conduction
        heat_from_sweat = sweat_rate * self.heat_loss_per_l
        dry_loss = max(0.0, core_temp - ambient_temp) * self.conduction_coeff
        heat_loss_rate = heat_from_sweat + dry_loss

        # Update cumulative state
        self.total_sweat += sweat_rate * duration_hr
        self.total_heat_loss += heat_loss_rate * duration_hr

        return {
            "sweat_rate": round(sweat_rate, 3),
            "heat_dissipated": round(heat_loss_rate * duration_hr, 2),
        }

    # ------------------------------------------------------------------
    # ODE compatibility methods
    def get_state(self) -> Dict[str, float]:
        return {
            "skin_sweat_total": self.total_sweat,
            "skin_heat_loss_total": self.total_heat_loss,
        }

    def set_state(self, state_dict: Dict[str, float]) -> None:
        self.total_sweat = state_dict["skin_sweat_total"]
        self.total_heat_loss = state_dict["skin_heat_loss_total"]

    def inject_override(self, inputs: Dict[str, Any]) -> None:
        """Store override inputs to be used on the next :meth:`step` call."""
        self.override_inputs = inputs

    def derivatives(self, t: float, state: Dict[str, float]) -> Dict[str, float]:
        """Derivatives for ODE integration of cumulative values."""

        core_temp = self._core_temp
        ambient_temp = self._ambient_temp
        cortisol = self._cortisol

        temp_diff = max(0.0, core_temp - self.vasodilation_temp_threshold)
        sweat_rate = min(self.sweat_rate_max, temp_diff * 1.2)
        sweat_rate *= 1.0 - 0.3 * cortisol

        heat_from_sweat = sweat_rate * self.heat_loss_per_l
        dry_loss = max(0.0, core_temp - ambient_temp) * self.conduction_coeff
        heat_loss_rate = heat_from_sweat + dry_loss

        return {
            "skin_sweat_total": sweat_rate,
            "skin_heat_loss_total": heat_loss_rate,
        }
