# Fichier : game/engine.py
# Gestion des écrans et de l'interface utilisateur (menus, affichage, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

# Annotations : Security import for forward references
from __future__ import annotations

import json
import random

# Deque for recent templates tracking (to avoid repetitions)
from collections import deque
from dataclasses import dataclass
from typing import List, Optional

# Imports needed for AI agents
from ai.agent import Agent, AgentConfig, load_templates
from ai.rules import PublicState
from game.structure_ai import Player

# TTS
from game.tts_helper import speak_text

# Data class for chat events
@dataclass
class ChatEvent:
    name_ia: str
    text: str
    show_name_ia: bool


# Main game engine class
class GameEngine:
    def __init__(self, num_players: int, seed: Optional[int] = None):
        if num_players < 6:
            raise ValueError("num_players must be >= 6")

        # Random generator with optional seed for reproducibility
        self.rng = random.Random(seed)

        self.day_count = 1
        self.phase = "JourDiscussion"

        with open("data/ai_names.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        self.ai_names = data["prenoms"]

        self.players: List[Player] = self._create_players(num_players)

        # Used to track the last night victim
        self._last_night_victim: Optional[int] = None

        # Track found wolves' names
        self.found_wolves_names: set[str] = set()

        # Create AI agents for each player
        self.templates = load_templates("data/dialogue_ai_template.json")
        self.agents = {}

        # Recent templates used for diversity (to avoid repetitions)
        self.recent_templates_global = deque(maxlen=80)
        self.recent_templates_by_cat = {}

        # Recent messages for context (to avoid repetition with the same message)
        self.recent_messages = deque(maxlen=60)

        # Initialize agents
        for p in self.players:
            # Create agent configuration
            cfg = AgentConfig(name=p.name, role=p.role)

            # Use different seed for each agent for variability
            self.agents[p.name] = Agent(
                cfg, self.templates, seed=self.rng.randrange(1_000_000)
            )
        # Public chat history
        self.public_chat_history: list[tuple[str, str]] = []

    # Picks a template without recent repetitions
    def _pick_template_no_repeat(self, category: str, templates: list[str]) -> str:
        # initialize recent tracking for category if needed
        if category not in self.recent_templates_by_cat:
            self.recent_templates_by_cat[category] = deque(maxlen=25)

        recent_cat = self.recent_templates_by_cat[category]
        recent_global = self.recent_templates_global

        # filter candidates not in recent lists
        candidates = [
            t for t in templates if t not in recent_cat and t not in recent_global
        ]
        if not candidates:
            candidates = [t for t in templates if t not in recent_cat] or templates

        # Choose one and update recent lists
        chosen = self.rng.choice(candidates)
        recent_cat.append(chosen)
        recent_global.append(chosen)
        return chosen

    # Creates players with assigned roles
    def _create_players(self, num_players: int) -> List[Player]:
        names = self.rng.sample(self.ai_names, num_players)
        num_wolves = max(1, num_players // 4)

        roles = ["loup"] * num_wolves + ["villageois"] * (num_players - num_wolves)
        self.rng.shuffle(roles)

        # Create Player instances
        return [
            Player(name=n, role=r, alive=True, note=0) for n, r in zip(names, roles)
        ]

    # Helpers to get alive player indexes
    def alive_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive]

    # Helpers to get alive wolf indexes
    def alive_wolf_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive and p.role == "loup"]

    # Helpers to get alive villager indexes
    def alive_villager_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive and p.role != "loup"]

    # Helpers to get all wolves' names
    def all_wolves_names(self) -> list[str]:
        return [p.name for p in self.players if p.role == "loup"]

    # Helpers to get found wolves' names as a sorted list
    def found_wolves_list(self) -> list[str]:
        # tri stable pour l'affichage
        return sorted(self.found_wolves_names)

    # Determines if there is a winner
    def get_winner(self) -> Optional[str]:
        wolves = len(self.alive_wolf_indexes())
        villagers = len(self.alive_villager_indexes())

        if wolves == 0:
            return "village"
        if wolves >= villagers:
            return "loups"
        return None

    # Kills a player by index
    def kill_player(self, index: int) -> None:
        p = self.players[index]
        p.alive = False
        p.note = 0  # reset note on death

    # Generates day discussion messages
    def _generate_day_discussion(self, n_messages: int = 10) -> list[ChatEvent]:
        alive_names = [p.name for p in self.players if p.alive]

        # Generate messages
        events: list[ChatEvent] = []
        for _ in range(n_messages):
            speaker = self.rng.choice(alive_names)
            agent = self.agents[speaker]

            # create public state for the agent
            state = PublicState(
                alive_names=alive_names,
                chat_history=self.public_chat_history,
                day=self.day_count,
            )

            agent.observe_public(state)

            # try to avoid repeating the same message recently
            for _try in range(3):
                msg = agent.decide_message(state)
                rendered = f"{speaker}:{msg}"
                if rendered not in self.recent_messages:
                    self.recent_messages.append(rendered)
                    break

            # fallback if still repeating
            else:
                msg = agent.decide_message(state)

            # engine records the message
            self.public_chat_history.append((speaker, msg))
            events.append(ChatEvent(name_ia=speaker, text=msg, show_name_ia=True))

            # ← Lecture audio du message
            speak_text(msg)

        return events

    # Starts the day phase with discussion
    def start_day(self) -> List[ChatEvent]:
        self.phase = "JourDiscussion"
        events = [ChatEvent("Système", f"Début du Jour {self.day_count}.", True)]
        events += self._generate_day_discussion(n_messages=8)

        return events

    # Starts the voting phase
    def start_vote(self) -> List[ChatEvent]:
        self.phase = "JourVote"
        return [
            ChatEvent(
                "Système",
                "Vote : clique sur le bouton bleu d'une IA vivante pour l'éliminer.",
                True,
            )
        ]

    # Casts a vote to eliminate a player
    def cast_vote(self, target_index: int) -> List[ChatEvent]:
        if self.phase != "JourVote":
            return []

        if target_index < 0 or target_index >= len(self.players):
            return []
        if not self.players[target_index].alive:
            return []

        self.kill_player(target_index)

        # If the eliminated player is a wolf, add to found wolves
        target = self.players[target_index]
        if target.role == "loup":
            self.found_wolves_names.add(target.name)

        events: List[ChatEvent] = []
        events.append(
            ChatEvent(
                "Système",
                f"Le village élimine {self.players[target_index].name}.",
                True,
            )
        )

        # Passe à la nuit directement
        self.phase = "Nuit"
        events.append(ChatEvent("???", "La nuit tombe…", False))
        events.append(ChatEvent("???", "…des pas dans l'ombre…", False))
        return events

    # Resolves the night and starts the next day
    def resolve_night_and_start_next_day(self) -> List[ChatEvent]:
        if self.phase != "Nuit":
            return []

        self._last_night_victim = None

        # Night : The wolves choose a victim
        candidates = self.alive_villager_indexes()
        if candidates:
            victim = self.rng.choice(candidates)
            self.kill_player(victim)
            self._last_night_victim = victim

        # Next day
        self.day_count += 1

        events: List[ChatEvent] = []
        if self._last_night_victim is not None:
            name = self.players[self._last_night_victim].name
            events.append(
                ChatEvent("Système", f"Au matin, on retrouve {name} mort.", True)
            )
        else:
            events.append(ChatEvent("Système", "Au matin, personne n'est mort…", True))

        # Start next day discussion
        events += self.start_day()
        return events

    # Advances the game phase
    def advance(self) -> List[ChatEvent]:
        if self.phase == "JourDiscussion":
            # If day 2 or later, go to vote
            if self.day_count >= 2:
                return self.start_vote()
            else:
                self.phase = "Nuit"
                return [
                    ChatEvent("???", "La nuit tombe…", False),
                    ChatEvent("???", "…des pas dans l'ombre…", False),
                ]

        if self.phase == "Nuit":
            return self.resolve_night_and_start_next_day()

        # No action for other phases
        return []
