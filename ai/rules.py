# Fichier : ai/rules.py
# Gestion des règles et contraintes de l'IA + système de suspicion
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

from __future__ import annotations
from dataclasses import dataclass
import random
from typing import Dict, List, Optional

# Data class representing the public state of the game
@dataclass
class PublicState:
    alive_names: List[str]
    chat_history: List[tuple[str, str]]  # (speaker, text)
    day: int

# Picks a target based on weighted suspicion levels (fonction faite par l'IA)
# Weighs candidates according to their suspicion levels and picks one randomly
def pick_target_weighted(rng: random.Random, weights: Dict[str, float], candidates: List[str]) -> Optional[str]:
    items = [(c, max(0.0, weights.get(c, 0.0))) for c in candidates]
    total = sum(w for _, w in items)
    if total <= 1e-9:
        return rng.choice(candidates) if candidates else None
    r = rng.random() * total
    acc = 0.0
    for name, w in items:
        acc += w
        if r <= acc:
            return name
    return items[-1][0] if items else None

# Chooses an action for a villager based on suspicion levels
def choose_action_for_villager(rng: random.Random, suspicion: Dict[str, float]) -> str:
    if not suspicion:
        return "hedge"

    top = max(suspicion.values())
    if top > 2.0:
        return rng.choices(["accuse", "question"], weights=[0.7, 0.3])[0]
    if top > 1.0:
        return rng.choices(["question", "accuse", "hedge"], weights=[0.5, 0.2, 0.3])[0]
    return rng.choices(["hedge", "question", "agree"], weights=[0.6, 0.25, 0.15])[0]

# Chooses an action for a wolf based on suspicion levels
def choose_action_for_wolf(rng: random.Random, suspicion: Dict[str, float]) -> str:
    if not suspicion:
        return rng.choice(["hedge", "deflect"])

    top = max(suspicion.values())
    if top > 1.5:
        return rng.choices(["accuse", "deflect", "agree"], weights=[0.55, 0.35, 0.10])[0]
    return rng.choices(["deflect", "hedge", "agree"], weights=[0.55, 0.30, 0.15])[0
    ]
