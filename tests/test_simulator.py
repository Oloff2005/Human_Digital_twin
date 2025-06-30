from hypothesis import given
from hypothesis.strategies import floats
from hdt.simulator import Simulator

@given(glucose=floats(min_value=60.0, max_value=180.0))
def test_glucose_variation_does_not_crash_sim(glucose):
    sim = Simulator()
    sim.inject_signal('glucose_level', glucose)
    sim.step()
