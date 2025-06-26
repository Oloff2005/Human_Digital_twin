class TimeManager:
    """
    Manages simulation time in minutes, hours, and days.
    Useful for circadian modeling and time-based processes.
    """

    def __init__(self, start_minute=0):
        self.minute = start_minute

    @property
    def hour(self):
        return (self.minute // 60) % 24

    @property
    def day(self):
        return self.minute // (60 * 24)

    def tick(self, step_minutes=60):
        """
        Advance time by a given step.

        Args:
            step_minutes (int): how many minutes to advance the clock
        """
        self.minute += step_minutes

    def reset(self):
        self.minute = 0

    def get_time_state(self):
        return {
            "minute": self.minute,
            "hour": self.hour,
            "day": self.day
        }
