from dataclasses import dataclass
from typing import List

@dataclass
class Connection:
    """Represents a directional link between two units."""
    origin: str
    destination: str


STREAM_MAP: List[Connection] = [
    Connection("Gut", "CardiovascularTransport"),
    Connection("CardiovascularTransport", "Liver"),
    Connection("CardiovascularTransport", "Muscle"),
    Connection("CardiovascularTransport", "Storage"),
    Connection("Liver", "Muscle"),
    Connection("Liver", "Storage"),
    Connection("BrainController", "HormoneRouter"),
    Connection("HormoneRouter", "Gut"),
    Connection("HormoneRouter", "CardiovascularTransport"),
    Connection("HormoneRouter", "Liver"),
    Connection("HormoneRouter", "Muscle"),
    Connection("HormoneRouter", "Storage"),
]

__all__ = ["Connection", "STREAM_MAP"]