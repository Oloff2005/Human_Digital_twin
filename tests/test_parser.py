import sys
import os
import json

# Step 1: Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Step 2: Import classes
from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer

# Step 3: Build absolute paths to your files
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
mapping_path = os.path.join(project_root, "hdt", "config", "wearable_mapping.json")
input_path = os.path.join(project_root, "data", "sample_inputs.json")

# Step 4: Parse wearable input
parser = InputParser(mapping_path)
parsed = parser.parse(input_path)

print("✅ Parsed Signals:")
print(json.dumps(parsed, indent=4))

# Step 5: Normalize parsed signals
normalizer = SignalNormalizer()
normalized = normalizer.normalize(parsed)

print("\n✅ Normalized Signals:")
print(json.dumps(normalized, indent=4))

