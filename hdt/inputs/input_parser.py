
import json

class InputParser:
    def __init__(self, mapping_path):
        with open(mapping_path, 'r') as file:
            self.mapping = json.load(file)

    def parse(self, input_json):
        """Parse wearable input JSON and map it to internal signals"""
        with open(input_json, 'r') as file:
            raw_data = json.load(file)

        parsed_signals = {}
        for signal, targets in self.mapping.items():
            if signal in raw_data:
                for target in targets:
                    if target not in parsed_signals:
                        parsed_signals[target] = {}
                    parsed_signals[target][signal] = raw_data[signal]
        return parsed_signals
