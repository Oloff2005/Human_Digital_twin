import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hdt.unit_operations.gut_reactor import GutReactor
from hdt.unit_operations.liver_metabolic_router import LiverMetabolicRouter
from hdt.unit_operations.muscle_effector import MuscleEffector
from hdt.unit_operations.fat_storage_reservoir import FatStorageReservoir
from hdt.engine.solver import ODESolver

# Initialize unit operations
gut = GutReactor(config={
    "digestion_efficiency": 0.9,
    "gastric_emptying_rate": 2.0,
    "absorption_delay": 10
})

liver = LiverMetabolicRouter(config={})

muscle = MuscleEffector(config={
    "resting_atp_demand": 2.5
})

storage = FatStorageReservoir(config={
    "max_glycogen": 400,
    "max_fat": 12000,
    "initial_glycogen": 300,
    "initial_fat": 8000
})

# Inputs
meal = {"carbs": 60, "fat": 20, "protein": 30, "fiber": 5, "water": 500}
hormones = {"insulin": 0.6, "glucagon": 0.4, "cortisol": 0.2}
duration_min = 60
duration_hr = duration_min / 60

# Digest meal through gut (absorbed nutrients)
absorbed = gut.digest(meal, duration_min=duration_min, hormones=hormones)["absorbed"]

# Route absorbed nutrients through liver
routed = liver.route(
    portal_input=absorbed,
    signals=hormones,
    microbiome_input=None,
    mobilized_reserves=None
)

# Load Muscle
muscle_inputs = routed["to_muscle_aerobic"]
muscle_inputs.update(routed["to_muscle_anaerobic"])
muscle.load_inputs(muscle_inputs, activity_level="moderate", hormones=hormones)

# Store energy in Storage
storage.step(signal_strength=hormones["glucagon"], duration_hr=duration_hr, storage_inputs=routed["to_storage"])

# Build initial state
initial_state = {
    **gut.get_state(),
    **liver.get_state(),
    **muscle.get_state(),
    **storage.get_state()
}

# Run simulation
solver = ODESolver(units=[gut, liver, muscle, storage])
results = solver.solve(t_span=(0, 10), y0=initial_state, t_eval=list(range(11)))

# Print output
for step in results:
    t = step["t"]
    state = step["state"]
    print(f"t={t:.1f} | " + " | ".join([f"{k}={v:.2f}" for k, v in state.items()]))
