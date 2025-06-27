import json

class InputParser:
    def __init__(self, mapping_path: str):
        """
        Initialize the InputParser with a wearable-to-model mapping.

        Args:
            mapping_path (str): Path to wearable_mapping.json
        """
        with open(mapping_path, 'r') as file:
            self.mapping = json.load(file)

    def parse(self, raw_data) -> dict:
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
            with open(raw_data, 'r') as f:
                raw_data = json.load(f)


        parsed_signals = {}

        for signal, targets in self.mapping.items():
            if signal in raw_data and raw_data[signal] is not None:
                for target in targets:
                    parsed_signals.setdefault(target, {})
                    parsed_signals[target][signal] = raw_data[signal]

        return parsed_signals
