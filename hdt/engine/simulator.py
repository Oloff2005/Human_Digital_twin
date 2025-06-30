from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from hdt.core.time_manager import TimeManager
from hdt.engine.solver import ODESolver
from hdt.inputs.input_parser import InputParser
from hdt.inputs.signal_normalizer import SignalNormalizer
from hdt.recommender.rule_engine import RuleEngine
from hdt.streams.stream import BidirectionalStreamManager, Stream
from hdt.streams.stream_map import BIDIRECTIONAL_PAIRS, STREAM_MAP, BidirectionalPair


class Simulator:
    """Coordinate unit operations and manage time progression."""

    def __init__(
        self,
        config: Dict[str, Any],
        wearable_inputs: Optional[Dict[str, Any]] = None,
        use_ode: bool = False,
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose
        self.use_ode = use_ode
        self.time = TimeManager()
        self.history: List[Dict[str, Any]] = []
        rules_path = (
            Path(__file__).resolve().parent.parent / "recommender" / "rules.yaml"
        )
        self.rule_engine = RuleEngine(
            mode="rule_based",
            rules_path=str(rules_path),
            rule_version="version_A",
        )

        # ------------------------------------------------------------------
        # Initialize unit operations
        # ------------------------------------------------------------------
        from hdt.unit_operations.brain_controller import BrainController
        from hdt.unit_operations.colon_microbiome_reactor import ColonMicrobiomeReactor
        from hdt.unit_operations.fat_storage_reservoir import FatStorageReservoir
        from hdt.unit_operations.gut_reactor import GutReactor
        from hdt.unit_operations.heart_circulation import HeartCirculation
        from hdt.unit_operations.hormone_router import HormoneRouter
        from hdt.unit_operations.kidney_reactor import KidneyReactor
        from hdt.unit_operations.liver_metabolic_router import LiverMetabolicRouter
        from hdt.unit_operations.lung_reactor import LungReactor
        from hdt.unit_operations.muscle_effector import MuscleEffector
        from hdt.unit_operations.pancreatic_valve import PancreaticValve
        from hdt.unit_operations.skin_thermoregulator import SkinThermoregulator
        from hdt.unit_operations.sleep_regulation_center import SleepRegulationCenter

        self.units: Dict[str, Any] = {
            "BrainController": BrainController(config.get("brain", {})),
            "Gut": GutReactor(config.get("gut", {})),
            "Colon": ColonMicrobiomeReactor(config.get("colon", {})),
            "Liver": LiverMetabolicRouter(config.get("liver", {})),
            "HeartCirculation": HeartCirculation(config.get("cardio", {})),
            "Kidney": KidneyReactor(config.get("kidney", {})),
            "Muscle": MuscleEffector(config.get("muscle", {})),
            "HormoneRouter": HormoneRouter(config.get("hormones", {})),
            "Lungs": LungReactor(config.get("lungs", {})),
            "Storage": FatStorageReservoir(config.get("storage", {})),
            "PancreaticValve": PancreaticValve(config.get("pancreas", {})),
            "Skin": SkinThermoregulator(config.get("skin", {})),
            "SleepRegulationCenter": SleepRegulationCenter(config.get("sleep", {})),
        }

        # Wearable input handling
        parser = InputParser("hdt/config/wearable_mapping.json")
        normalizer = SignalNormalizer()
        if wearable_inputs is not None:
            parsed = parser.parse(wearable_inputs)
            self.signals = normalizer.normalize(parsed)
        else:
            self.signals = {}

        # Stream map connections
        self.streams: Dict[tuple[str, str], Stream] = {
            (conn.origin, conn.destination): Stream(conn.origin, conn.destination)
            for conn in STREAM_MAP
        }

        # Bidirectional stream managers
        self.bidir_streams: Dict[frozenset[str], BidirectionalStreamManager] = {}
        for pair in BIDIRECTIONAL_PAIRS:
            manager = BidirectionalStreamManager(
                pair.a,
                pair.b,
                delay_ab=pair.delay_ab,
                delay_ba=pair.delay_ba,
            )
            self.bidir_streams[frozenset({pair.a, pair.b})] = manager

        # Optional ODE solver setup
        self.solver: Optional[ODESolver] = None
        if self.use_ode:
            ode_units = [u for u in self.units.values() if hasattr(u, "derivatives")]
            self.solver = ODESolver(ode_units)
            self.state: Dict[str, float] = {}
            for unit in ode_units:
                self.state.update(unit.get_state())

    # ------------------------------------------------------------------
    # Simulation helpers
    # ------------------------------------------------------------------
    def _record_state(self) -> Dict[str, Any]:
        snapshot: Dict[str, Any] = {"minute": self.time.minute}
        for name, unit in self.units.items():
            if hasattr(unit, "get_state"):
                snapshot[name] = unit.get_state()
        self.history.append(snapshot)
        return snapshot

    # ------------------------------------------------------------------
    def step(self, external_inputs: Optional[Dict[str, Any]] = None) -> None:
        external_inputs = external_inputs or {}

        if self.use_ode and self.solver is not None:
            start = self.time.minute
            result = self.solver.solve(
                t_span=(start, start + 1),
                y0=self.state,
                t_eval=[start, start + 1],
            )
            self.state = result[-1]["state"]
            for unit in self.solver.units:
                unit_state = {k: self.state[k] for k in unit.get_state().keys()}
                unit.set_state(unit_state)
        else:
            # ------------------------------------------------------------------
            # Discrete stepping sequence mirroring physiological flow
            # ------------------------------------------------------------------
            brain_out = self.units["BrainController"].step(
                {
                    "muscle_signals": external_inputs.get("muscle_signals", {}),
                    "gut_signals": external_inputs.get("gut_signals", {}),
                    "wearable_signals": self.signals.get("BrainController", {}),
                    "time_of_day": self.time.hour,
                }
            )
            self.streams[("BrainController", "HormoneRouter")].push(
                brain_out, self.time.minute
            )

            hr_inputs = {}
            for payload in self.streams[("BrainController", "HormoneRouter")].step(
                self.time.minute
            ):
                if isinstance(payload, dict):
                    hr_inputs.update(payload)
            # HormoneRouter expects plain hormone signals only
            nested = hr_inputs.pop("hormone_signals", {})
            hr_inputs.update(
                {k: v for k, v in nested.items() if isinstance(v, (int, float))}
            )
            hr_inputs = {
                k: v for k, v in hr_inputs.items() if isinstance(v, (int, float))
            }
            hormone_out = self.units["HormoneRouter"].step(hr_inputs)
            for conn in STREAM_MAP:
                if conn.origin == "HormoneRouter":
                    self.streams[(conn.origin, conn.destination)].push(
                        hormone_out, self.time.minute
                    )

            gut_inputs = external_inputs.get("meal", {})
            gut_out = self.units["Gut"].step(
                {"meal_input": gut_inputs, "duration_min": 60, "hormones": hormone_out}
            )
            self.streams[("Gut", "Liver")].push(gut_out["absorbed"], self.time.minute)

            colon_out = self.units["Colon"].step({"fiber_input": gut_out["residue"].get("fiber", 0)})

            portal_inputs = {}
            for payload in self.streams[("Gut", "Liver")].step(self.time.minute):
                if isinstance(payload, dict):
                    portal_inputs.update(payload)

            mobilized = self.units["Storage"].mobilize(
                signal_strength=hormone_out.get("glucagon", 0.5), duration_hr=1
            )

            liver_out = self.units["Liver"].route(
                portal_input=portal_inputs,
                microbiome_input=colon_out["scfa_output"],
                mobilized_reserves=mobilized["mobilized"],
                signals=hormone_out,
            )
            heart_payload = {
                "glucose": liver_out["to_muscle_aerobic"].get("glucose", 0),
                "fatty_acids": liver_out["to_muscle_aerobic"].get("fat", 0),
                "amino_acids": 0,
                "water": portal_inputs.get("water", 0),
            }
            self.streams[("Liver", "HeartCirculation")].push(
                heart_payload, self.time.minute
            )

            cv_inputs = {}
            for payload in self.streams[("Liver", "HeartCirculation")].step(
                self.time.minute
            ):
                if isinstance(payload, dict):
                    cv_inputs.update(payload)
            cardio_out = self.units["HeartCirculation"].step({"absorbed_nutrients": cv_inputs})

            muscle_inputs = {
                "glucose": cardio_out["to_systemic"].get("glucose", 0),
                "fat": cardio_out["to_systemic"].get("fatty_acids", 0),
            }

            muscle_out = self.units["Muscle"].metabolize(
                inputs=muscle_inputs,
                activity_level=external_inputs.get("activity_level", "rest"),
                hormones=hormone_out,
            )

            lung_out = self.units["Lungs"].exchange(
                duration_min=60,
                co2_in=muscle_out["exhaust"].get("co2", 0),
            )

            kidney_out = self.units["Kidney"].step(
                {
                    "blood_input": {
                        "urea": 5.0,
                        "water": cardio_out["to_systemic"].get("water", 0),
                    },
                    "duration_min": 60,
                }
            )

            skin_out = self.units["Skin"].regulate(
                core_temp=external_inputs.get("core_body_temperature", 36.8),
                ambient_temp=external_inputs.get("ambient_temperature", 22.0),
                hormones=hormone_out,
            )

            sleep_unit = self.units["SleepRegulationCenter"]
            sleep_unit.update_state(
                hours_since_last_sleep=external_inputs.get("hours_awake", 12)
            )
            sleep_out = sleep_unit.compute_sleep_signals(
                current_hour=self.time.hour,
                wearable_signals=self.signals.get("SleepRegulationCenter", {}),
            )

            self.units["Storage"].store(liver_out["to_storage"])

            if self.verbose:
                print(f"[t={self.time.minute}] Brain={brain_out} Gut={gut_out}")

        snapshot = self._record_state()
        recommendations = self.rule_engine.get_recommendations(snapshot)
        if self.verbose:
            print(f"[t={self.time.minute}] Recommendations={recommendations}")
        snapshot["recommendations"] = recommendations
        self.time.tick(60)

    # ------------------------------------------------------------------
    def run(
        self, steps: int, external_inputs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        for _ in range(steps):
            self.step(external_inputs)
        return self.history


if __name__ == "__main__":
    print("🚀 Human Digital Twin Simulation Started in Docker!")
    # Call your main simulation logic here
