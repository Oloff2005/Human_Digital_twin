"""Static map describing connections between unit operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class BidirectionalPair:
    """Defines a reversible link between two units with optional delays."""

    a: str
    b: str
    delay_ab: int = 0
    delay_ba: int = 0


@dataclass
class Connection:
    """Represents a directional link between two units."""

    origin: str
    destination: str


# Biologically realistic flow map for the Human Digital Twin simulation
STREAM_MAP: List[Connection] = [
    # Nutrient absorption via portal system
    Connection("Gut", "Liver"),  # Nutrients absorbed enter liver via portal vein
    Connection(
        "Liver", "HeartCirculation"
    ),  # Processed nutrients enter systemic circulation
    # Distribution to major organs and systems
    Connection("HeartCirculation", "Muscle"),
    Connection("HeartCirculation", "Storage"),
    Connection("HeartCirculation", "Brain"),
    Connection(
        "HeartCirculation", "Gut"
    ),  # Supplies blood back to the gut (e.g., oxygen, hormones)
    # Return pathways (waste products, metabolic byproducts)
    Connection("Muscle", "HeartCirculation"),  # CO₂, lactate return
    Connection(
        "Storage", "HeartCirculation"
    ),  # Mobilized energy (glucose, fatty acids)
    # Secondary nutrient redistribution
    Connection("Liver", "Muscle"),
    Connection("Liver", "Storage"),
    # Hormonal and control signal routing
    Connection("BrainController", "HormoneRouter"),
    Connection("HormoneRouter", "Gut"),
    Connection("HormoneRouter", "HeartCirculation"),
    Connection("HormoneRouter", "Liver"),
    Connection("HormoneRouter", "Muscle"),
    Connection("HormoneRouter", "Storage"),
    Connection("HormoneRouter", "Brain"),
]

# Reversible flows with potentially different delays in each direction
BIDIRECTIONAL_PAIRS: List[BidirectionalPair] = [
    BidirectionalPair("HeartCirculation", "Storage"),
    BidirectionalPair("Liver", "Muscle"),
]

__all__ = ["Connection", "BidirectionalPair", "STREAM_MAP", "BIDIRECTIONAL_PAIRS"]
