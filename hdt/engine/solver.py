from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Avoid heavy third party dependencies like numpy/scipy so that the test suite
# can run in a minimal environment.  The solver below implements a very simple
# explicit Euler integrator using only the Python standard library.

class ODESolver:
    """A very small ODE solver used in the tests.

    The solver expects a collection of unit operations which expose
    ``get_state``, ``set_state`` and ``derivatives`` methods.  It then performs
    a forward Euler integration across the provided ``t_eval`` grid.
    """

    def __init__(self, units: List[Any]):
        """
        Initialize with a list of unit operations.
        Each unit must have:
        - get_state(): returns {var_name: value}
        - set_state(state_dict)
        - derivatives(t, state_vector): returns [dy/dt]
        """
        self.units: List[Any] = units
        self.state_vars: List[str] = []
        self.var_to_unit: Dict[str, Any] = {}
        self._build_state_map()

    def _build_state_map(self) -> None:
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

    def solve(
        self,
        t_span: Tuple[float, float],
        y0: Dict[str, float],
        t_eval: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
      """Integrate the system using a simple Euler method."""

      if t_eval is None:
            t_eval = [t_span[0], t_span[1]]
      
      current_state = dict(y0)
      current_t = t_eval[0]
      results = []

      for next_t in t_eval:
            # Record the state at the beginning of the step
            results.append({"t": current_t, "state": dict(current_state)})

            dt = next_t - current_t
            if dt > 0:
                derivs = self._combined_derivatives(current_t, current_state)
                for var in self.state_vars:
                    current_state[var] += derivs[var] * dt
                current_t = next_t

      # Append the final state if the last evaluation time was beyond the
        # last recorded time point.
      if results and results[-1]["t"] != current_t:
            results.append({"t": current_t, "state": dict(current_state)})

      return results
