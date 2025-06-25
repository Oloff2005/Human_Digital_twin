from fastapi import FastAPI, UploadFile, File
import json
from hdt.engine.run_simulator import run_simulator
from hdt.config_loader import load_units_config, load_sim_params

app = FastAPI()

@app.post("/api/apple-health/upload")
async def upload_apple_health(file: UploadFile = File(...)):
    contents = await file.read()
    health_data = json.loads(contents)

    # Load simulation settings
    units_config = load_units_config("hdt/config/units_config_active.yaml")
    sim_params = load_sim_params("hdt/config/sim_params.yaml")

    # Run simulation
    result = run_simulator(health_data, units_config, sim_params)

    return {"status": "ok", "result": result}
