"""Abstract interface for unit operations used in the simulation."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseUnit(ABC):
    """Abstract base class for all unit operations."""

    @abstractmethod
    def step(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one simulation step using ``inputs``."""
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state to initial values."""
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Return a dictionary representing the current state."""
        raise NotImplementedError

    @abstractmethod
    def set_state(self, state_dict: Dict[str, Any]) -> None:
        """Set the internal state from ``state_dict``."""
        raise NotImplementedError

    def derivatives(self, t: float, state_dict: Dict[str, float]) -> Dict[str, float]:
        """Return time derivatives for ODE based simulation."""
        raise NotImplementedError("This unit does not implement ODE dynamics")
