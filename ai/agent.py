# Fichier : ai/agent.py
# Gestion de l'agent IA (décisions, comportements, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

from __future__ import annotations
import json
import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from ai.rules import PublicState, choose_action_for_villager, choose_action_for_wolf, pick_target_weighted

# Data class for agent configuration
@dataclass
class AgentConfig:
    name: str
    role: str  # "villageois" | "loup"
    personality: str = "neutre"  # pour plus tard


# Main AI agent class
class Agent:
    # Initializes the agent with configuration, templates, and optional seed
    def __init__(self, cfg: AgentConfig, templates: dict, seed: Optional[int] = None):
        self.name = cfg.name
        self.role = cfg.role
        self.personality = cfg.personality
        self.rng = random.Random(seed)

        self.templates = templates

        # Suspicion levels towards other players
        self.suspicion: Dict[str, float] = {}

    # Update suspicion based on public state
    def observe_public(self, state: PublicState):
        # init suspicion keys
        for n in state.alive_names:
            if n != self.name and n not in self.suspicion:
                self.suspicion[n] = 0.0

        # analyse recent messages (last 6 messages)
        recent = state.chat_history[-6:]
        for speaker, text in recent:
            low = text.lower()

            # speaker suspicion increase if they use suspect words
            if speaker != self.name and any(k in low for k in ["suspect", "louche", "cache", "bizarre"]):
                self.suspicion[speaker] = self.suspicion.get(speaker, 0.0) + 0.15

            # mentions of other players increase their suspicion
            for target in list(self.suspicion.keys()):
                if target in text:
                    self.suspicion[target] = self.suspicion.get(target, 0.0) + 0.10

        # clamp suspicion values between 0.0 and 5.0
        for k in list(self.suspicion.keys()):
            self.suspicion[k] = max(0.0, min(5.0, self.suspicion[k]))

    # Decide on a message to send based on the public state
    def decide_message(self, state: PublicState) -> str:
        # candidates for targeting
        candidates = [n for n in state.alive_names if n != self.name]
        if not candidates:
            return "…"

        if self.role == "villageois":
            action = choose_action_for_villager(self.rng, self.suspicion)
            bank = self.templates["villageois"].get(action, self.templates["villageois"]["hedge"])
        else:
            action = choose_action_for_wolf(self.rng, self.suspicion)
            bank = self.templates["loup"].get(action, self.templates["loup"]["hedge"])

        # choose target based on action type (random or weighted suspicion)
        if action in ("hedge",):
            target = self.rng.choice(candidates)
        else:
            target = pick_target_weighted(self.rng, self.suspicion, candidates) or self.rng.choice(candidates)

        # pick a template
        tpl = self.rng.choice(bank)

        # embellish the message
        common = self.templates.get("common", {})
        c = self.rng.choice(common.get("connectors", [""]))
        s = self.rng.choice(common.get("softeners", [""]))
        end = self.rng.choice(common.get("endings", [""]))

        return tpl.format(target=target, c=c, s=s, e=end)


    # Choose a night victim if the agent is a wolf
    def choose_night_victim(self, alive_names: List[str]) -> Optional[str]:
        candidates = [n for n in alive_names if n != self.name]
        return self.rng.choice(candidates) if candidates else None

# Utility function to load message templates from a JSON file
def load_templates(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
