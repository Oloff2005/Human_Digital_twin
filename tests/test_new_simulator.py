import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hdt.engine.simulator import Simulator
from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer


def test_simulator_runs_one_step():
    # Minimal unit configuration to avoid YAML dependency
    config = {
        'brain': {}, 'gut': {}, 'colon': {}, 'liver': {}, 'cardio': {},
        'kidney': {}, 'muscle': {}, 'hormones': {}, 'lungs': {},
        'storage': {}, 'pancreas': {}, 'skin': {}, 'sleep': {}
    }

    parser = InputParser(os.path.join('hdt', 'config', 'wearable_mapping.json'))
    parsed = parser.parse(os.path.join('data', 'sample_inputs.json'))
    signals = SignalNormalizer().normalize(parsed)
    sim = Simulator(config, wearable_inputs=signals, verbose=False)
    sim.step()
    assert len(sim.history) == 1