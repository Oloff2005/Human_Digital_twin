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

    def parse(self, raw_data: dict) -> dict:
        """
        Map incoming raw JSON data to internal physiological modules.

        Args:
            raw_data (dict): JSON data from Apple Health or another wearable

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
        parsed_signals = {}

        for signal, targets in self.mapping.items():
            if signal in raw_data:
                for target in targets:
                    if target not in parsed_signals:
                        parsed_signals[target] = {}
                    parsed_signals[target][signal] = raw_data[signal]

        return parsed_signals
