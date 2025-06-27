import unittest
from hdt.engine.simulator import Simulator

MINIMAL_CONFIG = {
    'brain': {},
    'gut': {},
    'colon': {},
    'liver': {},
    'cardio': {},
    'kidney': {},
    'muscle': {},
    'hormones': {},
    'lungs': {'oxygen_uptake_rate': 320, 'co2_exhale_rate': 250},
    'storage': {},
    'pancreas': {},
    'skin': {},
    'sleep': {},
}

class TestSimulatorClock(unittest.TestCase):
    def test_clock_advances_and_resets(self):
        sim = Simulator(config=MINIMAL_CONFIG, initial_inputs={}, verbose=False)
        self.assertEqual(sim.clock.get_time_state()['minute'], 0)
        sim.step()
        self.assertEqual(sim.clock.get_time_state()['minute'], 60)
        sim.clock.reset()
        self.assertEqual(sim.clock.get_time_state()['minute'], 0)

if __name__ == '__main__':
    unittest.main()