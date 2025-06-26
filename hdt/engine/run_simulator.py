import json
from hdt.engine.simulator import Simulator
from hdt.config_loader import load_units_config, load_sim_params
from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer

def run_simulator(config_path, input_path, steps=1, verbose=False):
    """
    Loads config and inputs, initializes Simulator, and runs simulation.

    Args:
        config_path (str): path to unit config YAML file
        input_path (str): path to wearable input JSON file
        steps (int): number of simulation steps
        verbose (bool): whether to enable verbose debug output

    Returns:
        list: simulation output log
    """
    # Load configurations
    config = load_units_config(config_path)
    sim_params = load_sim_params("hdt/config/sim_params.yaml")


    # Parse and normalize input
    parser = InputParser("hdt/config/wearable_mapping.json")
    parsed = parser.parse(input_path)
    normalizer = SignalNormalizer()
    normalized_inputs = normalizer.normalize(parsed)

    # Initialize and run
    sim = Simulator(config=config, initial_inputs=normalized_inputs, verbose=verbose)
    results = sim.run(steps=steps)

    return results
