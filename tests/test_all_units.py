import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

from hdt.unit_operations.gut_reactor import GutReactor
from hdt.unit_operations.colon_microbiome_reactor import ColonMicrobiomeReactor
from hdt.unit_operations.liver_metabolic_router import LiverMetabolicRouter
from hdt.unit_operations.muscle_effector import MuscleEffector
from hdt.unit_operations.fat_storage_reservoir import FatStorageReservoir 
from hdt.unit_operations.kidney_reactor import KidneyReactor
from hdt.unit_operations.lung_reactor import LungReactor
from hdt.unit_operations.brain_controller import BrainController
from hdt.unit_operations.skin_thermoregulator import SkinThermoregulator
from hdt.unit_operations.sleep_regulation_center import SleepRegulationCenter
from hdt.unit_operations.pancreatic_valve import PancreaticValve
from hdt.unit_operations.hormone_router import HormoneRouter  

class TestAllUnits(unittest.TestCase):
    def test_colon_microbiome_reactor(self):
        colon = ColonMicrobiomeReactor({})
        result = colon.process_residue(15)
        self.assertIn("scfa_output", result)

    def test_storage_unit(self):
        store = FatStorageReservoir({})
        result = store.store({"glucose": 20, "fatty_acids": 10})
        self.assertIn("glycogen", result)
        self.assertIn("fat", result)

    def test_kidney_reactor(self):
        kidney = KidneyReactor({})
        result = kidney.filter({"urea": 12.0, "water": 600})
        self.assertIn("urine_output", result)

    def test_lung_reactor(self):
        lung = LungReactor({})
        result = lung.exchange(350, 300)
        self.assertIn("co2_exhaled", result)

    def test_brain_controller(self):
        brain = BrainController({})
        out = brain.integrate_inputs(
            muscle_signals={"fatigue_signal": 4, "lactate": 1.2},
            gut_signals={"butyrate_signal": 1.0, "total_scfa": 2.2},
            wearable_signals={"hr": 65, "hrv": 70, "sleep_quality": 0.85},
            time_of_day=21
        )
        self.assertIn("insulin", out)

    def test_brain_manual_override(self):
        brain = BrainController({})
        brain.set_manual_override("stress_level", 0.9)
        self.assertEqual(brain.stress_level, 0.9)

    def test_hormone_router(self):
        router = HormoneRouter()
        signals = {
            "insulin": 0.8,
            "glucagon": 0.5,
            "cortisol": 0.6,
            "melatonin": 0.7
        }
        result = router.route(signals)
        self.assertLess(result["insulin"], 0.8)
        self.assertLess(result["melatonin"], 0.7)
        self.assertEqual(result, router.step(signals))

    def test_skin_thermoregulator(self):
        skin = SkinThermoregulator({})
        result = skin.regulate(core_temp=38.0, ambient_temp=30, hormones={"cortisol": 0.3})
        self.assertIn("sweat_loss", result)

    def test_pancreatic_valve(self):
        pancreas = PancreaticValve({})
        out = pancreas.regulate(blood_glucose_mmol_per_L=5.6, rate_of_change=0.1)
        self.assertIn("insulin", out)

if __name__ == '__main__':
    unittest.main()
