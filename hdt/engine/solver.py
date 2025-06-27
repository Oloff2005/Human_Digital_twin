# solver.py

from typing import List, Dict, Tuple


class ODESolver:
    def __init__(self, units: List):
        """
        Initialize with a list of unit operations.
        Each unit must have:
        - get_state(): returns {var_name: value}
        - set_state(state_dict)
        - derivatives(t, state_vector): returns [dy/dt]
        """
        self.units = units
        self.state_vars = []
        self.var_to_unit = {}
        self._build_state_map()

    def _build_state_map(self):
        """Maps each state variable to its owning unit."""
        for unit in self.units:
            state = unit.get_state()
            for var in state:
                self.state_vars.append(var)
                self.var_to_unit[var] = unit

    def _combined_derivatives(self, t: float, state: Dict[str, float]) -> Dict[str, float]:
        """Compute derivatives for the full system as a flat dictionary."""
        derivatives = {}
        for unit in self.units:
            unit_state = {v: state[v] for v in unit.get_state().keys()}
            derivs = unit.derivatives(t, unit_state)
            derivatives.update(derivs)
        return derivatives

    def solve(self, t_span: Tuple[float, float], y0: Dict[str, float], t_eval=None):
        """Simple Euler solver to avoid heavy dependencies."""
        if t_eval is None:
            t_eval = [t_span[0], t_span[1]]
        current_state = dict(y0)
        current_t = t_eval[0]
        results = []

        for next_t in t_eval:
            dt = next_t - current_t
            if dt > 0:
                derivs = self._combined_derivatives(current_t, current_state)
                for var in self.state_vars:
                    current_state[var] += derivs[var] * dt
                current_t = next_t
            results.append({"t": next_t, "state": dict(current_state)})

        return results
