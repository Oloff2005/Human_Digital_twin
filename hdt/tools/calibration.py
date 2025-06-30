from datetime import datetime
from typing import Dict, Iterable


def calibrate(
    inputs: Iterable[float], observed_outputs: Iterable[float], *, adjust: bool = False
) -> Dict[str, float]:
    """Compare predicted outputs to observed values and compute error metrics.

    Parameters
    ----------
    inputs: Iterable[float]
        Predicted outputs from the model.
    observed_outputs: Iterable[float]
        Actual observed measurements.
    adjust: bool, optional
        If True, adjust model parameters based on the error (placeholder).

    Returns
    -------
    Dict[str, float]
        Dictionary containing ``mae`` and ``rmse``.
    """
    predicted = [float(x) for x in inputs]
    observed = [float(x) for x in observed_outputs]

    if len(predicted) != len(observed):
        raise ValueError("inputs and observed_outputs must have the same shape")

    diffs = [abs(p - o) for p, o in zip(predicted, observed)]
    mae = sum(diffs) / len(diffs)
    rmse = (sum((p - o) ** 2 for p, o in zip(predicted, observed)) / len(diffs)) ** 0.5

    log_line = f"{datetime.now().isoformat()}\tMAE={mae:.4f}\tRMSE={rmse:.4f}\n"
    with open("calibration_log.txt", "a") as log_file:
        log_file.write(log_line)

    if adjust:
        # Placeholder for parameter adjustment logic. In a real implementation
        # this would update model parameters based on the computed errors.
        pass

    return {"mae": mae, "rmse": rmse}


if __name__ == "__main__":
    example_pred = [1.0, 2.5, 3.0, 4.2]
    example_obs = [0.8, 2.7, 2.9, 4.1]
    metrics = calibrate(example_pred, example_obs)
    print("Calibration metrics:", metrics)
