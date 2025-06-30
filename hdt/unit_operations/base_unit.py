from abc import ABC, abstractmethod


class BaseUnit(ABC):
    """Abstract base class for all unit operations."""

    @abstractmethod
    def step(self, inputs):
        """Execute one simulation step using ``inputs``."""
        raise NotImplementedError

    @abstractmethod
    def reset(self):
        """Reset internal state to initial values."""
        raise NotImplementedError

    @abstractmethod
    def get_state(self):
        """Return a dictionary representing the current state."""
        raise NotImplementedError

    @abstractmethod
    def set_state(self, state_dict):
        """Set the internal state from ``state_dict``."""
        raise NotImplementedError

    def derivatives(self, t, state_dict):
        """Return time derivatives for ODE based simulation."""
        raise NotImplementedError("This unit does not implement ODE dynamics")
