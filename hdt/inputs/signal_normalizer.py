
class SignalNormalizer:
    def __init__(self):
        # Define normalization rules or coefficients here if needed
        pass

    def normalize(self, parsed_signals):
        """
        Takes in parsed signals (dict by unit) and applies normalization.
        """
        normalized_signals = {}

        for unit, signals in parsed_signals.items():
            normalized_signals[unit] = {}

            for signal, value in signals.items():
                normalized_value = self._normalize_signal(signal, value)
                normalized_signals[unit][signal] = normalized_value

        return normalized_signals

    def _normalize_signal(self, signal, value):
        """
        Normalization rules per signal.
        This is where you'd apply scaling, baseline adjustment, z-score, etc.
        """
        if signal == "heart_rate":
            return value / 100.0  # normalize to 0–1 scale
        elif signal == "sleep_score":
            return value / 100.0
        elif signal == "stress_score":
            return value / 100.0
        elif signal == "training_readiness":
            return value / 100.0
        elif signal == "oxygen_saturation":
            return value / 100.0
        elif signal == "resting_heart_rate":
            return value / 100.0
        elif signal == "parasympathetic_tone":
            return value  # already normalized (0–1)
        else:
            return value  # no normalization applied by default