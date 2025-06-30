import json
import os
from datetime import datetime

HISTORY_PATH = "data/health_history.json"


def log_health_snapshot(raw_data: dict, sim_result: dict) -> None:
    """
    Appends a new health + simulation record to the history log.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": raw_data,
        "result": sim_result,
    }

    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w") as f:
            json.dump([entry], f, indent=2)
    else:
        with open(HISTORY_PATH, "r+") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
