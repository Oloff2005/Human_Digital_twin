from typing import Any, Dict, Optional

from pydantic import BaseModel


class AppleHealthInput(BaseModel):
    heart_rate: Optional[float] = None
    resting_heart_rate: Optional[float] = None
    parasympathetic_tone: Optional[float] = None
    sleep_score: Optional[int] = None
    sleep_duration: Optional[float] = None
    steps: Optional[int] = None
    activity_load: Optional[float] = None
    cardiorespiratory_fitness: Optional[float] = None
    calories_burned: Optional[float] = None
    respiration_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    stress_score: Optional[int] = None
    core_body_temperature: Optional[float] = None
    skin_temperature: Optional[float] = None
    training_readiness: Optional[int] = None
    recovery_time_estimate: Optional[int] = None


class InputValidator:
    """Validates and converts raw wearable JSON input using the ``AppleHealthInput`` schema."""

    model = AppleHealthInput

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a dictionary of validated values or raise ``ValidationError``."""
        return cls.model(**data).dict(exclude_none=True)
