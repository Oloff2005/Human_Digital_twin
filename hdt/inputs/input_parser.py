from __future__ import annotations

import json
import math
from typing import Any, Dict, Union, cast

from utils.logging_utils import setup_logger

logger = setup_logger(__name__)


class InputParser:
    def __init__(self, mapping_path: str) -> None:
        """
        Initialize the InputParser with a wearable-to-model mapping.

        Args:
            mapping_path (str): Path to wearable_mapping.json
        """
        with open(mapping_path, "r") as file:
            self.mapping: Dict[str, list[str]] = json.load(file)

    def parse(self, raw_data: Union[Dict[str, Any], str]) -> Dict[str, Dict[str, Any]]:
        """
        Map incoming raw JSON data to internal physiological modules. ``raw_data``
        may be a dictionary or a path to a JSON file. Any ``None`` values are
        ignored so downstream units do not need to handle them.

         Args:
             raw_data (dict or str): JSON data from Apple Health or another wearable

         Returns:
             dict: Structured signal dictionary for unit operations, e.g.:
                 {
                     "BrainController": {
                         "heart_rate": 72,
                         "hrv": 85,
                         "sleep_score": 90
                     },
                     "MuscleReactor": {
                         "steps": 11000
                     }
                 }
        """

        # Allow passing a file path for convenience
        if isinstance(raw_data, str):
            with open(raw_data, "r") as f:
                raw_data = json.load(f)

        raw_dict = cast(Dict[str, Any], raw_data)

        parsed_signals: Dict[str, Dict[str, Any]] = {}

        for signal, targets in self.mapping.items():
            value = raw_dict.get(signal)
            if value is None:
                logger.warning("%s missing or None; skipping", signal)
                continue
            if isinstance(value, (int, float)) and math.isnan(value):
                logger.warning("%s is NaN; skipping", signal)
                continue
            for target in targets:
                parsed_signals.setdefault(target, {})
                parsed_signals[target][signal] = value

        return parsed_signals
