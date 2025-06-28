from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from hdt.engine.simulator import Simulator
from hdt.config_loader import load_units_config, load_sim_params
from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer
from hdt.validation.input_schema import AppleHealthInput


BASE_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = BASE_DIR / "hdt"

CONFIG_PATH = PACKAGE_ROOT / "config" / "units_config_active.yaml"
SIM_PARAMS_PATH = PACKAGE_ROOT / "config" / "sim_params.yaml"
MAPPING_PATH = PACKAGE_ROOT / "config" / "wearable_mapping.json"


app = FastAPI()

# Simulation globals
simulator: Optional[Simulator] = None
latest_state: Optional[dict] = None
latest_recommendations: List[str] = []
wearable_data: Optional[dict] = None

# Parser for wearable data
parser = InputParser(str(MAPPING_PATH))
normalizer = SignalNormalizer()


class MealInput(BaseModel):
    carbs: float = 0.0
    fat: float = 0.0
    protein: float = 0.0
    fiber: float = 0.0
    water: float = 0.0


class WorkoutInput(BaseModel):
    activity_level: str = "rest"


class SleepInput(BaseModel):
    hours: float = 8.0


class RunRequest(BaseModel):
    meal: MealInput
    workout: WorkoutInput | None = WorkoutInput()
    sleep: SleepInput | None = SleepInput()


@app.on_event("startup")
def startup() -> None:
    """Initialize simulator on application startup."""
    global simulator
    config = load_units_config(str(CONFIG_PATH))
    load_sim_params(str(SIM_PARAMS_PATH))  # validate config
    simulator = Simulator(config=config, wearable_inputs=None, verbose=False)


@app.post("/run")
def run_simulation(payload: RunRequest) -> dict:
    """Run one simulation step with the provided lifestyle inputs."""
    global latest_state, latest_recommendations
    if simulator is None:
        return {"error": "Simulator not initialized"}

    external = {
        "meal": payload.meal.model_dump(),
        "activity_level": payload.workout.activity_level if payload.workout else "rest",
        "hours_awake": max(0.0, 24 - (payload.sleep.hours if payload.sleep else 0.0)),
    }

    simulator.step(external)
    latest_state = simulator.history[-1]
    latest_recommendations = latest_state.get("recommendations", [])
    return latest_state


@app.post("/data")
def ingest_data(data: AppleHealthInput) -> dict:
    """Store wearable data and update simulator input signals."""
    global wearable_data
    wearable_data = data.model_dump(exclude_none=True)

    structured = parser.parse(wearable_data)
    normalized = normalizer.normalize(structured)

    if simulator is not None:
        simulator.signals = normalized

    return {"status": "ok"}


@app.get("/state")
def get_state() -> dict:
    """Return the most recent simulator state."""
    return latest_state or {}


@app.get("/recommendations")
def get_recommendations() -> dict:
    """Return the latest lifestyle recommendations."""
    return {"recommendations": latest_recommendations}