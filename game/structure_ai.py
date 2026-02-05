# Fichier : game/structure_ai.py

# Annotations : Security import for forward references
from __future__ import annotations
from dataclasses import dataclass


# Player data structure for the game
@dataclass
class Player:
    name: str
    role: str  # "villageois" | "loup"
    alive: bool = True
    note: int = 0  # AI's internal note about this player (0-3)
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb"