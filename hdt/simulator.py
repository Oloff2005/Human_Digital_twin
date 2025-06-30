from __future__ import annotations

from typing import Any, Dict, Optional

from hdt.engine.simulator import Simulator as _Simulator

DEFAULT_CONFIG = {
    "brain": {},
    "gut": {},
    "colon": {},
    "liver": {},
    "cardio": {},
    "kidney": {},
    "muscle": {},
    "hormones": {},
    "lungs": {"oxygen_uptake_rate": 320, "co2_exhale_rate": 250},
    "storage": {},
    "pancreas": {},
    "skin": {},
    "sleep": {},
}


class Simulator(_Simulator):
    """Convenience wrapper providing a default minimal configuration."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        wearable_inputs: Optional[Dict[str, Any]] = None,
        use_ode: bool = False,
        verbose: bool = False,
    ) -> None:
        config = config or DEFAULT_CONFIG
        super().__init__(
            config=config,
            wearable_inputs=wearable_inputs,
            use_ode=use_ode,
            verbose=verbose,
        )

    def inject_signal(self, signal_name: str, value: Any) -> None:
        """Inject a wearable signal value for the next step."""
        self.signals.setdefault("BrainController", {})
        self.signals["BrainController"][signal_name] = value


__all__ = ["Simulator"]
