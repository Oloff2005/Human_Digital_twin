import json
from pathlib import Path

from hdt.engine.simulator import Simulator
from hdt.config_loader import load_units_config, load_sim_params


def main():
    # Ensure log directory exists
    log_dir = Path("calibration_logs")
    log_dir.mkdir(exist_ok=True)

    # Load raw wearable inputs
    input_path = Path("data") / "sample_inputs.json"
    with open(input_path, "r", encoding="utf-8") as f:
        raw_inputs = json.load(f)

    # Simulator will handle parsing and normalization internally

    # Load baseline targets
    baseline = load_units_config("data/baseline_states.yaml")

    # Load unit configs and simulation parameters
    config = load_units_config("hdt/config/units_config_active.yaml")
    load_sim_params("hdt/config/sim_params.yaml")

    # Run 60 minute simulation (one step)
    sim = Simulator(config=config, wearable_inputs=raw_inputs, verbose=False)
    history = sim.run(steps=1)
    snapshot = history[-1]

    # Collect outputs for comparison
    outputs = {
        "liver_glycogen": snapshot.get("Liver", {}).get("liver_glycogen"),
        "heart_rate": raw_inputs.get("heart_rate"),
    }

    # Compute errors only for keys available in baseline
    errors = {}
    for key, output_val in outputs.items():
        if key in baseline and output_val is not None:
            errors[key] = abs(output_val - baseline[key])

    mae = sum(errors.values()) / len(errors) if errors else None

    results = {
        "outputs": outputs,
        "baseline": {k: baseline[k] for k in outputs.keys() if k in baseline},
        "errors": errors,
        "mae": mae,
    }

    # Print comparison results
    for k, err in errors.items():
        print(f"{k}: output={outputs[k]} baseline={baseline[k]} error={err}")
    if mae is not None:
        print(f"Mean Absolute Error: {mae}")

    # Save to log file
    with open(log_dir / "last_run.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()