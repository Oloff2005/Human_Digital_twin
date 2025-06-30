"""Simple JSON logging utilities for ingestion examples."""

import json
import os
from datetime import datetime
from typing import Any, Dict

HISTORY_PATH = "data/health_history.json"


def log_health_snapshot(raw_data: Dict[str, Any], sim_result: Dict[str, Any]) -> None:
    """
    Appends a new health + simulation record to the history log.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": raw_data,
        "result": sim_result,
    }

    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump([entry], f, indent=2)
    else:
        with open(HISTORY_PATH, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)
