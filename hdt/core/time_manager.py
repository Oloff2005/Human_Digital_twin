"""Simple utility to track simulation time in minutes, hours, and days."""

from __future__ import annotations

from typing import Dict


class TimeManager:
    """
    Manages simulation time in minutes, hours, and days.
    Useful for circadian modeling and time-based processes.
    """

    def __init__(self, start_minute: int = 0) -> None:
        self.minute: int = start_minute

    @property
    def hour(self) -> int:
        return (self.minute // 60) % 24

    @property
    def day(self) -> int:
        return self.minute // (60 * 24)

    def tick(self, step_minutes: int = 60) -> None:
        """
        Advance time by a given step.

        Args:
            step_minutes (int): how many minutes to advance the clock
        """
        self.minute += step_minutes

    def reset(self) -> None:
        self.minute = 0

    def get_time_state(self) -> Dict[str, int]:
        return {
            "minute": self.minute,
            "hour": self.hour,
            "day": self.day,
        }
