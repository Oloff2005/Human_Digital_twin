"""Data structures for passing information between unit operations."""

from __future__ import annotations

from collections import deque
from typing import Any, Deque, List, Tuple


class Stream:
    """Unidirectional biochemical or signal flow between two unit operations."""

    def __init__(self, source: str, target: str, delay: int = 0) -> None:
        self.source = source
        self.target = target
        self.delay = delay
        self._buffer: Deque[Tuple[int, Any]] = deque()

    def push(self, payload: Any, timestamp: int) -> None:
        deliver_time = timestamp + self.delay
        self._buffer.append((deliver_time, payload))

    def pull(self, timestamp: int) -> List[Any]:
        ready: List[Any] = []
        while self._buffer and self._buffer[0][0] <= timestamp:
            _, data = self._buffer.popleft()
            ready.append(data)
        return ready

    def step(self, timestamp: int) -> List[Any]:
        return self.pull(timestamp)

    def __repr__(self) -> str:
        return f"<Stream {self.source}→{self.target} delay={self.delay}>"


class BidirectionalStreamManager:
    """A reversible stream between two unit operations."""

    def __init__(
        self, unit_a: str, unit_b: str, delay_ab: int = 0, delay_ba: int = 0
    ) -> None:
        """Creates two directional streams: A→B and B→A."""
        self.ab = Stream(unit_a, unit_b, delay=delay_ab)
        self.ba = Stream(unit_b, unit_a, delay=delay_ba)

    def push(self, source: str, payload: Any, timestamp: int) -> None:
        """Push payload from source to the other unit."""
        if source == self.ab.source:
            self.ab.push(payload, timestamp)
        elif source == self.ba.source:
            self.ba.push(payload, timestamp)
        else:
            raise ValueError(
                f"Source '{source}' is not part of this bidirectional stream."
            )

    def pull(self, target: str, timestamp: int) -> List[Any]:
        """Pull payloads targeted at the given unit."""
        if target == self.ab.target:
            return self.ab.pull(timestamp)
        elif target == self.ba.target:
            return self.ba.pull(timestamp)
        else:
            raise ValueError(
                f"Target '{target}' is not part of this bidirectional stream."
            )

    def step(self, unit_name: str, timestamp: int) -> List[Any]:
        """Simulation-friendly step function for one unit."""
        return self.pull(unit_name, timestamp)

    def __repr__(self) -> str:
        return f"<BidirectionalStream {self.ab.source}⇄{self.ab.target}>"
