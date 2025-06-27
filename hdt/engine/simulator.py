class Simulator:
    def __init__(self, config, initial_inputs, verbose=False):
        from hdt.unit_operations.brain_controller import BrainController
        from hdt.unit_operations.gut_reactor import GutReactor
        from hdt.unit_operations.colon_microbiome_reactor import ColonMicrobiomeReactor
        from hdt.unit_operations.liver_metabolic_router import LiverMetabolicRouter
        from hdt.unit_operations.cardiovascular_transport import CardiovascularTransport
        from hdt.unit_operations.kidney_reactor import KidneyReactor
        from hdt.unit_operations.muscle_effector import MuscleEffector
        from hdt.unit_operations.hormone_router import HormoneRouter
        from hdt.unit_operations.lung_reactor import LungReactor
        from hdt.unit_operations.storage_unit import StorageUnit
        from hdt.unit_operations.pancreatic_valve import PancreaticValve
        from hdt.unit_operations.skin_thermoregulator import SkinThermoregulator
        from hdt.unit_operations.sleep_regulation_center import SleepRegulationCenter
        from hdt.streams.stream import Stream

        self.units = {
            "brain": BrainController(config["brain"]),
            "gut": GutReactor(config["gut"]),
            "colon": ColonMicrobiomeReactor(config["colon"]),
            "liver": LiverMetabolicRouter(config["liver"]),
            "cardio": CardiovascularTransport(config["cardio"]),
            "kidney": KidneyReactor(config["kidney"]),
            "muscle": MuscleEffector(config["muscle"]),
            "hormones": HormoneRouter(config.get("hormones", {})),
            "lungs": LungReactor(**config["lungs"]),
            "storage": StorageUnit(config["storage"]),
            "pancreas": PancreaticValve(config["pancreas"]),
            "skin": SkinThermoregulator(config["skin"]),
            "sleep": SleepRegulationCenter(config["sleep"])
        }

        self.initial_inputs = initial_inputs
        self.time = 0
        self.history = []
        self.verbose = verbose

    def step(self):
        inputs = self.initial_inputs.copy()

        brain_out = self.units["brain"].step(
            muscle_signals=inputs.get("muscle_signals", {}),
            gut_signals=inputs.get("gut_signals", {}),
            wearable_signals=inputs.get("wearable_signals", {}),
            time_of_day=self.time % 24
        )

        gut_out = self.units["gut"].step(
            meal_input=inputs.get("meal", {}),
            duration_min=60,
            hormones=brain_out
        )

        colon_out = self.units["colon"].step(gut_out["residue"].get("fiber", 0))

        hormone_out = self.units["hormones"].resolve(brain_out)

        cardio_out = self.units["cardio"].step(gut_out["absorbed"])

        mobilized = self.units["storage"].mobilize(
            signal_strength=hormone_out["glucagon"], duration_hr=1
        )

        liver_out = self.units["liver"].route(
            portal_input=cardio_out["to_liver"],
            microbiome_input=colon_out["scfa_output"],
            mobilized_reserves=mobilized["mobilized"],
            signals=hormone_out
        )

        muscle_out = self.units["muscle"].metabolize(
            inputs=liver_out["to_muscle_aerobic"],
            activity_level=inputs.get("activity_level", "rest"),
            hormones=hormone_out
        )

        lung_out = self.units["lungs"].exchange(
            duration_min=60,
            co2_in=muscle_out["exhaust"].get("co2", 0)
        )

        kidney_out = self.units["kidney"].step(
            {"urea": 5.0, "water": cardio_out["to_systemic"].get("water", 0)}
        )

        skin_out = self.units["skin"].regulate(
            core_temp=inputs.get("core_body_temperature", 36.8),
            ambient_temp=inputs.get("ambient_temperature", 22.0),
            hormones=hormone_out
        )

        self.units["sleep"].update_state(hours_since_last_sleep=inputs.get("hours_awake", 12))
        sleep_out = self.units["sleep"].compute_sleep_signals(
            current_hour=self.time % 24,
            wearable_signals=inputs.get("wearable_signals", {})
        )

        self.units["storage"].store(liver_out["to_storage"])

        self.history.append({
            "time": self.time,
            "brain": brain_out,
            "gut": gut_out,
            "colon": colon_out,
            "cardio": cardio_out,
            "liver": liver_out,
            "muscle": muscle_out,
            "lungs": lung_out,
            "kidney": kidney_out,
            "skin": skin_out,
            "sleep": sleep_out,
            "storage": mobilized
        })

        if self.verbose:
            print(f"\n[Step {self.time}] Simulation Outputs:")
            print(f"🧠 Brain: {brain_out}")
            print(f"🍽️ Gut: {gut_out}")
            print(f"🧬 Colon: {colon_out}")
            print(f"💉 Hormones: {hormone_out}")
            print(f"❤️ Cardio: {cardio_out}")
            print(f"🧪 Liver: {liver_out}")
            print(f"💪 Muscle: {muscle_out}")
            print(f"🌬️ Lungs: {lung_out}")
            print(f"🫁 Kidney: {kidney_out}")
            print(f"🌡️ Skin: {skin_out}")
            print(f"🛏️ Sleep: {sleep_out}")
            print(f"🪙 Storage: {self.units['storage'].current_glycogen:.1f}g glycogen, {self.units['storage'].current_fat:.1f}g fat")
            print("—" * 80)

        self.time += 1

    def run(self, steps=1):
        for _ in range(steps):
            self.step()
        return self.history
