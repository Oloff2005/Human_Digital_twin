from hdt.engine.simulator import Simulator as _Simulator

DEFAULT_CONFIG = {
    'brain': {}, 'gut': {}, 'colon': {}, 'liver': {}, 'cardio': {},
    'kidney': {}, 'muscle': {}, 'hormones': {},
    'lungs': {'oxygen_uptake_rate': 320, 'co2_exhale_rate': 250},
    'storage': {}, 'pancreas': {}, 'skin': {}, 'sleep': {}
}

class Simulator(_Simulator):
    """Convenience wrapper providing a default minimal configuration."""

    def __init__(self, config=None, wearable_inputs=None, use_ode=False, verbose=False):
        config = config or DEFAULT_CONFIG
        super().__init__(config=config, wearable_inputs=wearable_inputs, use_ode=use_ode, verbose=verbose)

    def inject_signal(self, signal_name: str, value):
        """Inject a wearable signal value for the next step."""
        self.signals.setdefault('BrainController', {})
        self.signals['BrainController'][signal_name] = value

__all__ = ["Simulator"]
