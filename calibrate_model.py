import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import types

try:  # pragma: no cover - optional dependency
    import matplotlib.pyplot as plt_module
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    plt_module = None

plt_module: Optional[types.ModuleType]

from hdt.engine.simulator import Simulator
from hdt.config_loader import load_units_config, load_sim_params

def create_plots(
    history: List[Dict[str, Any]],
    baseline: Dict[str, Any],
    heart_rate_input: float,
    output_path: Path,
) -> None:
    """Generate calibration plots.

    Args:
        history (list[dict]): simulation history snapshots.
        baseline (dict): baseline target values.
        heart_rate_input (float): input heart rate value.
        output_path (Path): location to save the image.
    """

    if plt_module is None:
        # Matplotlib not available; skip plotting
        return
    
    minutes = [snap.get("minute", 0) for snap in history]
    glycogen_pred = [snap.get("Liver", {}).get("liver_glycogen") for snap in history]
    heart_rate_pred = [heart_rate_input for _ in history]

    fig, axes = plt_module.subplots(2, 1, figsize=(8, 8))

    # Predicted vs baseline values
    axes[0].plot(minutes, glycogen_pred, label="predicted_liver_glycogen")
    axes[0].hlines(
        baseline.get("liver_glycogen"), minutes[0], minutes[-1],
        colors="r", linestyles="--", label="baseline_liver_glycogen"
    )
    axes[0].set_ylabel("Liver Glycogen")

    ax_hr = axes[0].twinx()
    ax_hr.plot(minutes, heart_rate_pred, color="g", label="predicted_heart_rate")
    ax_hr.hlines(
        baseline.get("heart_rate"), minutes[0], minutes[-1],
        colors="orange", linestyles="--", label="baseline_heart_rate"
    )
    ax_hr.set_ylabel("Heart Rate")

    lines1, labels1 = axes[0].get_legend_handles_labels()
    lines2, labels2 = ax_hr.get_legend_handles_labels()
    axes[0].legend(lines1 + lines2, labels1 + labels2, loc="best")
    axes[0].set_title("Predicted vs Baseline")

    # Error over time
    glycogen_err = [abs(p - baseline.get("liver_glycogen", 0)) for p in glycogen_pred]
    hr_err = [abs(p - baseline.get("heart_rate", 0)) for p in heart_rate_pred]
    axes[1].plot(minutes, glycogen_err, label="liver_glycogen_error")
    axes[1].plot(minutes, hr_err, label="heart_rate_error")
    axes[1].set_xlabel("Minute")
    axes[1].set_ylabel("Absolute Error")
    axes[1].legend()
    axes[1].set_title("Error Over Time")

    fig.tight_layout()
    fig.savefig(output_path)
    plt_module.close(fig)

def run_calibration(save_logs: bool = True) -> Dict[str, Any]:
    """Run a single calibration step and optionally save logs."""
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
        "liver_glucose": snapshot.get("Liver", {}).get("liver_glucose"),
        "liver_glycogen": snapshot.get("Liver", {}).get("liver_glycogen"),
        "heart_rate": raw_inputs.get("heart_rate"),
    }

    # Compute errors only for keys available in baseline
    errors = {}
    for key, output_val in outputs.items():
        baseline_val = baseline.get(key, 0.0)
        if output_val is not None:
            errors[key] = abs(output_val - baseline_val)

    mae = sum(errors.values()) / len(errors) if errors else None

    results = {
        "outputs": outputs,
        "baseline": {k: baseline[k] for k in outputs.keys() if k in baseline},
        "errors": errors,
        "mae": mae,
    }

    # Print comparison results
    for k, err in errors.items():
        base_val = baseline.get(k, 0.0)
        print(f"{k}: output={outputs[k]} baseline={base_val} error={err}")
    if mae is not None:
        print(f"Mean Absolute Error: {mae}")

    if save_logs:
        # Save to log file
        with open(log_dir / "last_run.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        # Generate calibration plots
        plot_path = log_dir / "predicted_vs_actual.png"
        create_plots(history, baseline, raw_inputs.get("heart_rate"), plot_path)

    return results


def main() -> None:
    run_calibration(save_logs=True)

if __name__ == "__main__":
    main()