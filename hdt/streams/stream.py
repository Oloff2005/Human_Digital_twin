"""Stream utilities for inter-unit communication.

This module defines a simple :class:`Stream` class that represents a
uni-directional connection between two unit operations.  Each stream
can buffer payloads that are pushed into it and releases them after a
configurable delay.  The design is intentionally lightweight so that
unit tests can run without heavy dependencies.
"""

from collections import deque
from typing import Any, Deque, List, Tuple


class Stream:
    """Directional biochemical or signal flow between unit operations."""

    def __init__(self, source: str, target: str, delay: int = 0) -> None:
        """Create a new stream.

        Parameters
        ----------
        source: str
            Name of the originating unit.
        target: str
            Name of the destination unit.
        delay: int, optional
            Number of simulation steps before a pushed payload becomes
            available to the target.  Defaults to ``0``.
        """
        self.source = source
        self.target = target
        self.delay = delay
        self._buffer: Deque[Tuple[int, Any]] = deque()

    def push(self, payload: Any, timestamp: int) -> None:
        """Push ``payload`` into the stream.

        The payload will become available ``delay`` steps after the given
        ``timestamp``.
        """
        deliver_time = timestamp + self.delay
        self._buffer.append((deliver_time, payload))

    def pull(self, timestamp: int) -> List[Any]:
        """Retrieve all payloads whose delivery time is <= ``timestamp``."""
        ready: List[Any] = []
        while self._buffer and self._buffer[0][0] <= timestamp:
            _, data = self._buffer.popleft()
            ready.append(data)
        return ready

    def step(self, timestamp: int) -> List[Any]:
        """Simulation-friendly interface returning ready payloads."""
        return self.pull(timestamp)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<Stream {self.source}→{self.target} delay={self.delay}>"
