from pathlib import Path

from hdt.validation.input_schema import AppleHealthInput
from pydantic import ValidationError
from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer
from hdt.config_loader import load_units_config, load_sim_params
from hdt.engine.run_simulator import run_simulator
from hdt.ingestion.logger import log_health_snapshot
from fastapi import FastAPI, UploadFile, File
import json

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent

app = FastAPI()

@app.post("/api/apple-health/upload")
async def upload_apple_health(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        raw_data = json.loads(contents)
        parsed = AppleHealthInput(**raw_data).dict(exclude_none=True)
    except ValidationError as e:
        return {"status": "error", "message": str(e)}

    # Parse & normalize signals
    mapping_path = PACKAGE_ROOT / "config" / "wearable_mapping.json"
    parser = InputParser(str(mapping_path))
    normalizer = SignalNormalizer()

    structured = parser.parse(parsed)
    normalized = normalizer.normalize(structured)

    # Load configs
    units_config = load_units_config(str(PACKAGE_ROOT / "config" / "units_config_active.yaml"))
    sim_params = load_sim_params(str(PACKAGE_ROOT / "config" / "sim_params.yaml"))

    # Run simulation
    result = run_simulator(normalized, units_config, sim_params)

    # Log snapshot to history
    log_health_snapshot(parsed, result)

    return {"status": "ok", "result": result}
