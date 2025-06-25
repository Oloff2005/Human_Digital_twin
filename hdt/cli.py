# hdt/cli.py

import argparse
import json
from hdt.engine.run_simulator import run_simulator

def main():
    parser = argparse.ArgumentParser(description="Run the Human Digital Twin simulation.")
    parser.add_argument("--input", type=str, required=True, help="Path to input JSON file")
    parser.add_argument("--steps", type=int, default=10, help="Number of simulation steps")

    args = parser.parse_args()

    # Load input JSON
    with open(args.input, "r") as f:
        input_data = json.load(f)

    # Run the simulation
    result = run_simulator(input_data, steps=args.steps)

    # Print summary output
    print("\n🧠 Final Digital Twin State:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
