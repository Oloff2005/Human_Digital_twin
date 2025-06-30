from .base_unit import BaseUnit


class BrainController(BaseUnit):
    def __init__(self, config):
        """Central logic hub for hormonal and behavioral control."""

        self.cortisol_threshold = config.get("cortisol_threshold", 0.65)
        self.stress_decay_rate = config.get("stress_decay_rate", 0.07)
        self.circadian_baseline = config.get("circadian_baseline", 1.0)

        # Internal state
        self.stress_level = 0.0
        self.hunger_level = 0.5
        self.sleep_pressure = 0.0
        self.time_of_day = 0  # hour 0–23

        # Optional output overrides
        self._override = {}

    def reset(self):
        """Reset internal controller state."""
        self.stress_level = 0.0
        self.hunger_level = 0.5
        self.sleep_pressure = 0.0
        self.time_of_day = 0
        self._override = {}

    def integrate_inputs(
        self, muscle_signals, gut_signals, wearable_signals, time_of_day
    ):
        """
        Combines physiological inputs and wearable data into control outputs.

        Args:
            muscle_signals (dict): {'fatigue_signal': x, 'lactate': y}
            gut_signals (dict): {'butyrate_signal': x, 'total_scfa': y}
            wearable_signals (dict): {'hr': bpm, 'hrv': ms, 'sleep_quality': 0–1}
            time_of_day (int): 0–23 clock hour

        Returns:
            dict: {
                'insulin': 0–1,
                'glucagon': 0–1,
                'cortisol': 0–1,
                'circadian_tone': 0–1,
                'digestive_signal': 0–1,
                'muscle_signal': 0–1
            }
        """
        self.time_of_day = time_of_day

        fatigue = muscle_signals.get("fatigue_signal", 0)
        poor_sleep = 1.0 - wearable_signals.get("sleep_quality", 0.8)
        hrv = wearable_signals.get("hrv", 50)
        butyrate = gut_signals.get("butyrate_signal", 0)

        stress_input = fatigue + poor_sleep + (60 - hrv) / 100 - (butyrate * 0.1)
        self.stress_level = max(
            0.0, self.stress_level * (1 - self.stress_decay_rate) + stress_input
        )

        # Cortisol production
        cortisol = min(1.0, self.stress_level * self.cortisol_threshold)

        # Circadian tone calculation
        circadian_peak = 23
        circadian_tone = (
            max(0.0, 1 - abs(time_of_day - circadian_peak) / 12)
            * self.circadian_baseline
        )

        # Hormone levels
        insulin = 0.6 if fatigue < 5 and poor_sleep < 0.3 else 0.4
        glucagon = 1.0 - insulin

        # Derived signals
        digestive_signal = circadian_tone * (1 - cortisol * 0.3)
        muscle_signal = insulin * (1 - cortisol * 0.2)

        signals = {
            "insulin": insulin,
            "glucagon": glucagon,
            "cortisol": cortisol,
            "circadian_tone": circadian_tone,
            "digestive_signal": digestive_signal,
            "muscle_signal": muscle_signal,
        }

        # Apply rule-based prioritization
        signals = self.apply_priority_rules(signals)

        return signals

    def apply_priority_rules(self, signals):
        """
        Applies hardcoded priority rules for control logic.
        """
        if signals["cortisol"] > 0.7:
            signals["digestive_signal"] *= 0.5
            signals["muscle_signal"] *= 0.7

        if signals["circadian_tone"] > 0.8 and self.time_of_day >= 20:
            signals["digestive_signal"] *= 1.2

        return signals

    # ------------------------------------------------------------------
    # New control routing logic
    def route_control_signals(self, wearable_signals, metabolic_state):
        """Process wearable and metabolic inputs into control outputs."""
        stress_score = wearable_signals.get("stress_score", 0.0)
        sleep_score = wearable_signals.get("sleep_score", 0.8)

        ghrelin = metabolic_state.get("ghrelin", 0.5)
        leptin = metabolic_state.get("leptin", 0.5)

        # Update internal states
        self.stress_level = max(
            0.0,
            self.stress_level * (1 - self.stress_decay_rate) + stress_score,
        )

        self.hunger_level = max(0.0, min(1.0, ghrelin * (1 - leptin)))
        self.sleep_pressure = max(
            0.0, self.sleep_pressure * 0.9 + (1 - sleep_score) * 0.1
        )

        cortisol = min(1.0, self.stress_level * self.cortisol_threshold)
        hormone_signals = {
            "cortisol": round(cortisol, 3),
            "ghrelin": round(self.hunger_level, 3),
            "melatonin": round(self.sleep_pressure, 3),
        }

        activity_intensity = min(1.0, wearable_signals.get("steps", 0) / 10000)
        sleep_trigger = self.sleep_pressure > 0.7

        outputs = {
            "hormone_signals": hormone_signals,
            "activity_intensity": activity_intensity,
            "sleep_trigger": sleep_trigger,
        }

        # Apply overrides if provided
        for key, value in self._override.items():
            outputs[key] = value

        return outputs

    def inject_override(self, override_dict):
        """Override output signals in ``route_control_signals``."""
        self._override = override_dict or {}

    def get_state(self):
        return {
            "stress_level": self.stress_level,
            "hunger_level": self.hunger_level,
            "sleep_pressure": self.sleep_pressure,
            "time_of_day": self.time_of_day,
        }

    def set_state(self, state_dict):
        self.stress_level = state_dict.get("stress_level", self.stress_level)
        self.hunger_level = state_dict.get("hunger_level", self.hunger_level)
        self.sleep_pressure = state_dict.get("sleep_pressure", self.sleep_pressure)
        self.time_of_day = state_dict.get("time_of_day", self.time_of_day)

    def set_manual_override(self, state_name, value):
        """
        Manually override internal states like stress_level or time_of_day.
        """
        if hasattr(self, state_name):
            setattr(self, state_name, value)

    def step(
        self,
        muscle_signals=None,
        gut_signals=None,
        wearable_signals=None,
        time_of_day=None,
        metabolic_state=None,
    ):
        """Execute one control step.

        This keeps backward compatibility with the original signature while also
        supporting the new ``route_control_signals`` interface.
        """

        wearable_signals = wearable_signals or {}
        metabolic_state = metabolic_state or {}

        if time_of_day is not None:
            self.time_of_day = time_of_day

        legacy = (
            muscle_signals is not None
            or gut_signals is not None
            or time_of_day is not None
        )

        outputs = {}
        if legacy:
            outputs.update(
                self.integrate_inputs(
                    muscle_signals or {},
                    gut_signals or {},
                    wearable_signals,
                    self.time_of_day,
                )
            )

        outputs.update(self.route_control_signals(wearable_signals, metabolic_state))
        return outputs
