import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hdt.engine.solver import ODESolver

class ExampleUnit:
    def __init__(self):
        self.glucose = 100.0  # initial mg/dL
        self.insulin = 10.0   # arbitrary units

    def get_state(self):
        return {
            "glucose": self.glucose,
            "insulin": self.insulin
        }

    def set_state(self, state_dict):
        self.glucose = state_dict["glucose"]
        self.insulin = state_dict["insulin"]

    def derivatives(self, t, state):
        k = 0.1  # decay constant
        return {
            "glucose": -k * state["glucose"],
            "insulin": 0.0
        }


# Create unit and solver
unit = ExampleUnit()
solver = ODESolver(units=[unit])

# Initial state
y0 = unit.get_state()

# Solve ODE from t=0 to t=10
result = solver.solve(t_span=(0, 10), y0=y0, t_eval=[i for i in range(11)])

# Print results
for step in result:
    t = step["t"]
    glucose = step["state"]["glucose"]
    insulin = step["state"]["insulin"]
    print(f"t={t:.1f} | Glucose={glucose:.2f} | Insulin={insulin:.2f}")
