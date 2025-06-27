from dataclasses import dataclass
from typing import List

@dataclass
class Connection:
    """Represents a directional link between two units."""
    origin: str
    destination: str


STREAM_MAP: List[Connection] = [
    Connection("Gut", "HeartCirculation"),
    Connection("HeartCirculation", "Liver"),
    Connection("HeartCirculation", "Muscle"),
    Connection("HeartCirculation", "Storage"),
    Connection("Liver", "Muscle"),
    Connection("Liver", "Storage"),
    Connection("BrainController", "HormoneRouter"),
    Connection("HormoneRouter", "Gut"),
    Connection("HormoneRouter", "HeartCirculation"),
    Connection("HormoneRouter", "Liver"),
    Connection("HormoneRouter", "Muscle"),
    Connection("HormoneRouter", "Storage"),
]

__all__ = ["Connection", "STREAM_MAP"]