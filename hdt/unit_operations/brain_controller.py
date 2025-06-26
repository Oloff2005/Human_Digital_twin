class BrainController:
    def __init__(self, config):
        """
        Simulates integration of stress, circadian, and energy signals.

        Args:
            config (dict): {
                'cortisol_threshold': (float) stress sensitivity,
                'stress_decay_rate': (float) how fast stress dissipates,
                'circadian_baseline': (float) baseline circadian tone
            }
        """
        self.cortisol_threshold = config.get("cortisol_threshold", 0.65)
        self.stress_decay_rate = config.get("stress_decay_rate", 0.07)
        self.circadian_baseline = config.get("circadian_baseline", 1.0)

        # Internal state
        self.stress_level = 0.0
        self.time_of_day = 0  # hour 0–23

    def integrate_inputs(self, muscle_signals, gut_signals, wearable_signals, time_of_day):
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
        self.stress_level = max(0.0, self.stress_level * (1 - self.stress_decay_rate) + stress_input)

        # Cortisol production
        cortisol = min(1.0, self.stress_level * self.cortisol_threshold)

        # Circadian tone calculation
        circadian_peak = 23
        circadian_tone = max(0.0, 1 - abs(time_of_day - circadian_peak) / 12) * self.circadian_baseline

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
            "muscle_signal": muscle_signal
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

    def set_manual_override(self, state_name, value):
        """
        Manually override internal states like stress_level or time_of_day.
        """
        if hasattr(self, state_name):
            setattr(self, state_name, value)

    def step(self, muscle_signals, gut_signals, wearable_signals, time_of_day):
        """
        Execute one simulation step for the brain controller.

        Returns:
            dict: Signals for the next unit
        """
        return self.integrate_inputs(muscle_signals, gut_signals, wearable_signals, time_of_day)
