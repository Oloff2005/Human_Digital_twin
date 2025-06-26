# solver.py

from typing import List, Dict, Tuple, Callable
import numpy as np
from scipy.integrate import solve_ivp


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

    def _combined_derivatives(self, t, y):
        """
        Flattened derivative vector for all units.
        """
        # Map flat y to {var_name: value}
        state_dict = dict(zip(self.state_vars, y))
        dydt = []

        for var in self.state_vars:
            unit = self.var_to_unit[var]
            # Build unit-specific state
            unit_state = {v: state_dict[v] for v in unit.get_state().keys()}
            derivs = unit.derivatives(t, unit_state)
            dydt.append(derivs[var])  # extract only the needed var

        return dydt

    def solve(self, t_span: Tuple[float, float], y0: Dict[str, float], t_eval=None):
        """
        Solves the ODE system over time t_span with initial state y0.
        """
        y0_list = [y0[var] for var in self.state_vars]

        sol = solve_ivp(
            fun=self._combined_derivatives,
            t_span=t_span,
            y0=y0_list,
            t_eval=t_eval,
            method="RK45",  # could use "LSODA" for stiffness
            vectorized=False,
        )

        # Map back to dict format for each time step
        results = []
        for i, t in enumerate(sol.t):
            state_at_t = {var: sol.y[j][i] for j, var in enumerate(self.state_vars)}
            results.append({"t": t, "state": state_at_t})

        return results
