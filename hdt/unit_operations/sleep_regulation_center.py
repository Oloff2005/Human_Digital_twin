class SleepRegulationCenter:
    def __init__(self, config):
        """
        Models melatonin production and sleep pressure.

        Args:
            config (dict): {
                - melatonin_release_rate (0–1)
                - circadian_peak_time (int, 0–23)
                - sleep_drive_gain (float)
            }
        """
        self.melatonin_release_rate = config.get("melatonin_release_rate", 0.35)
        self.circadian_peak_time = config.get("circadian_peak_time", 23)
        self.sleep_drive_gain = config.get("sleep_drive_gain", 1.4)

        # State
        self.hours_awake = 0

    def update_state(self, hours_since_last_sleep):
        self.hours_awake = hours_since_last_sleep

    def compute_sleep_signals(self, current_hour, wearable_signals=None):
        """
        Calculates melatonin output and sleep pressure based on circadian rhythm.

        Args:
            current_hour (int): Clock time (0–23)
            wearable_signals (dict): {
                - sleep_debt (0–1),
                - light_exposure (lux or 0–1 scaled),
                - activity_level (0–1)
            }

        Returns:
            dict: {
                'melatonin': 0–1,
                'sleep_drive': 0–1,
                'sleep_signal': 0–1
            }
        """
        if wearable_signals is None:
            wearable_signals = {}

        light_exposure = wearable_signals.get("light_exposure", 0.3)
        sleep_debt = wearable_signals.get("sleep_debt", 0.2)
        activity_level = wearable_signals.get("activity_level", 0.4)

        # Melatonin curve peaks at circadian peak time
        circadian_offset = abs(current_hour - self.circadian_peak_time)
        circadian_factor = max(0.0, 1.0 - circadian_offset / 12.0)

        melatonin = self.melatonin_release_rate * circadian_factor * (1.0 - light_exposure)

        # Sleep drive increases with hours awake + activity level + sleep debt
        drive = (self.hours_awake / 18.0 + activity_level * 0.4 + sleep_debt) * self.sleep_drive_gain
        sleep_drive = min(1.0, drive)

        sleep_signal = min(1.0, melatonin * 0.7 + sleep_drive * 0.8)

        return {
            "melatonin": round(melatonin, 3),
            "sleep_drive": round(sleep_drive, 3),
            "sleep_signal": round(sleep_signal, 3)
        }

    def step(self, current_hour, wearable_signals=None):
        """
        Simulation step interface for sleep regulation.

        Returns:
            dict: Sleep-related outputs
        """
        return self.compute_sleep_signals(current_hour, wearable_signals)
