import argparse
import json
import os
import sys

# Allow running this script directly without installing the package
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from hdt.engine.run_simulator import run_simulator

def main():
    parser = argparse.ArgumentParser(description="Run the Human Digital Twin simulation.")
    parser.add_argument("--input", type=str, required=True, help="Path to input JSON file")
    parser.add_argument("--steps", type=int, default=10, help="Number of simulation steps")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug output")
    parser.add_argument("--profile", type=str, default="beginner", choices=["beginner", "active", "athlete"], help="Simulation profile")

    args = parser.parse_args()

    # Choose correct config path
    config_path = f"hdt/config/units_config_{args.profile}.yaml"

    # Run the simulation
    result = run_simulator(
        config_path=config_path,
        input_path=args.input,
        steps=args.steps,
        verbose=args.verbose
    )

    # Print summary output
    print("\n🧠 Final Digital Twin State:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
