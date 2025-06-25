import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

from hdt.unit_operations.gut_reactor import GutReactor
from hdt.unit_operations.colon_microbiome_reactor import ColonMicrobiomeReactor
from hdt.unit_operations.liver_metabolic_router import LiverMetabolicRouter
from hdt.unit_operations.muscle_effector import MuscleEffector
from hdt.unit_operations.storage_unit import StorageUnit
from hdt.unit_operations.kidney_reactor import KidneyReactor
from hdt.unit_operations.lung_reactor import LungReactor
from hdt.unit_operations.brain_controller import BrainController
from hdt.unit_operations.skin_thermoregulator import SkinThermoregulator
from hdt.unit_operations.sleep_regulation_center import SleepRegulationCenter
from hdt.unit_operations.pancreatic_valve import PancreaticValve
from hdt.unit_operations.hormone_router import HormoneRouter  # NEW

class TestAllUnits(unittest.TestCase):
    def test_gut_reactor(self):
        gut = GutReactor({"digestion_efficiency": 0.9, "gastric_emptying_rate": 2.0, "absorption_delay": 10})
        result = gut.digest({"carbs": 60, "fat": 20, "protein": 30, "fiber": 10, "water": 300}, hormones={"circadian_tone": 1.0, "cortisol": 0.1})
        self.assertIn("absorbed", result)

    def test_colon_microbiome_reactor(self):
        colon = ColonMicrobiomeReactor({})
        result = colon.process_residue(15)
        self.assertIn("scfa_output", result)

    def test_liver_metabolic_router(self):
        liver = LiverMetabolicRouter({})
        output = liver.route({
            "glucose": 70,
            "fatty_acids": 50,
            "ketones": 5,
            "scfa": 3,
            "amino_acids": 20,
            "glycogen": 30,
            "triglycerides": 40
        })
        self.assertIn("to_muscle_aerobic", output)
        self.assertIn("to_muscle_anaerobic", output)

    def test_muscle_effector(self):
        muscle = MuscleEffector({})
        result = muscle.metabolize({"glucose": 60, "fat": 30}, activity_level="moderate", duration_min=45, hormones={"insulin": 0.7, "cortisol": 0.2})
        self.assertIn("substrate_used", result)

    def test_storage_unit(self):
        store = StorageUnit({})
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
            "digestive_signal": 0.9
        }
        result = router.resolve(signals)
        self.assertLess(result["insulin"], 0.8)
        self.assertLess(result["digestive_signal"], 0.9)

    def test_skin_thermoregulator(self):
        skin = SkinThermoregulator({})
        result = skin.regulate(core_temp=38.0, ambient_temp=30, hormones={"cortisol": 0.3})
        self.assertIn("sweat_loss", result)

    def test_sleep_regulation(self):
        sleep = SleepRegulationCenter({})
        sleep.update_state(hours_since_last_sleep=14)
        result = sleep.compute_sleep_signals(current_hour=22, wearable_signals={"light_exposure": 0.2, "sleep_debt": 0.3})
        self.assertIn("melatonin", result)

    def test_pancreatic_valve(self):
        pancreas = PancreaticValve({})
        out = pancreas.regulate(blood_glucose_mmol_per_L=5.6, rate_of_change=0.1)
        self.assertIn("insulin", out)

if __name__ == '__main__':
    unittest.main()
