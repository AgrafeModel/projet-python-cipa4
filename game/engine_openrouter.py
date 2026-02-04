# Fichier : game/engine_openrouter.py
# Gestion du moteur de jeu avec OpenRouter API
# Note : Commentaires en anglais pour uniformité avec engine.py.

from __future__ import annotations

import json
import os
import random
from collections import deque
from dataclasses import dataclass
from typing import List, Optional

from ai.client import OpenRouterClient, OpenRouterClientConfig
from game.structure_ai import Player
from game.agent import Agent
from game.context_manager import GameContextManager

# Data class for chat events
@dataclass
class ChatEvent:
    name_ia: str
    text: str
    show_name_ia: bool


# Main game engine class with OpenRouter
class GameEngine:
    def __init__(self, num_players: int, seed: Optional[int] = None):
        if num_players < 6:
            raise ValueError("num_players must be >= 6")

        # Random generator with optional seed for reproducibility
        self.rng = random.Random(seed)

        self.day_count = 1
        self.phase = "JourDiscussion"

        # Load AI names
        with open("data/ai_names.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.ai_names = data["prenoms"]

        # Initialize OpenRouter client
        key = os.getenv("OPENROUTER_API_KEY")
        if key is None:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        self.client = OpenRouterClient(OpenRouterClientConfig(key))
        self.context_manager = GameContextManager()

        # Initialize players and roles
        self.players: List[Player] = self._create_players(num_players)

        # Used to track the last night victim
        self._last_night_victim: Optional[int] = None

        # Track found wolves' names
        self.found_wolves_names: set[str] = set()

        # Create AI agents for each player (using OpenRouter agents)
        self.agents = {}
        for p in self.players:
            agent = Agent(p.name, p.role)  # Using the OpenRouter Agent
            self.agents[p.name] = agent

        # Initialize the game context
        self._initialize_game_context()

        # Set player roles in context manager for filtering
        for player in self.players:
            self.context_manager.set_player_role(player.name, player.role)

        # Public chat history
        self.public_chat_history: list[tuple[str, str]] = []

        # Recent messages for context (to avoid repetition)
        self.recent_messages = deque(maxlen=60)

    # Creates players with assigned roles
    def _create_players(self, num_players: int) -> List[Player]:
        names = self.rng.sample(self.ai_names, num_players)
        num_wolves = max(1, num_players // 4)

        # Map roles to match the OpenRouter agent expectations
        role_mapping = {
            "loup": "Loup-Garou",
            "villageois": "Villageois"
        }

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

    # Initialize the game context with initial state
    def _initialize_game_context(self):
        # Add initial game state to context
        alive_players = [p.name for p in self.players if p.alive]
        initial_context = {
            "type": "game_start",
            "content": f"Période: JourDiscussion. Jour {self.day_count}. Joueurs vivants: {', '.join(alive_players)}. La partie commence!"
        }
        self.context_manager.add_global_context(initial_context)

        # Add role information to each player's private context
        for player in self.players:
            if player.role == "loup":
                wolves = [p.name for p in self.players if p.role == "loup"]
                role_info = {
                    "type": "role_info",
                    "content": f"Tu es un Loup-Garou. Tes alliés loups sont: {', '.join([w for w in wolves if w != player.name])}."
                }
            else:
                role_info = {
                    "type": "role_info",
                    "content": f"Tu es un Villageois. Ton objectif est d'identifier et éliminer les Loups-Garous."
                }
            self.context_manager.add_player_context(player.name, role_info)

    # Update context with current game state
    def _update_game_state_context(self):
        alive_players = [p.name for p in self.players if p.alive]
        dead_players = [p.name for p in self.players if not p.alive]

        state_context = {
            "type": "game_state",
            "content": f"Période: {self.phase}. Jour {self.day_count}. Joueurs vivants: {', '.join(alive_players)}. Joueurs morts: {', '.join(dead_players) if dead_players else 'Aucun'}."
        }
        self.context_manager.add_global_context(state_context)

    # Generates day discussion messages using OpenRouter
    def _generate_day_discussion(self, n_messages: int = 10) -> list[ChatEvent]:
        # Update game state context before discussion
        self._update_game_state_context()

        alive_names = [p.name for p in self.players if p.alive]

        # Generate messages using OpenRouter
        events: list[ChatEvent] = []
        for _ in range(n_messages):
            speaker_name = self.rng.choice(alive_names)
            agent = self.agents[speaker_name]

            try:
                # Get current phase for context
                current_phase = self.phase

                # Use the agent's play method to generate discussion
                current_play = agent.play(current_phase, self.client, self.context_manager)
                msg = current_play.dialogue

                # Try to avoid repeating the same message recently
                rendered = f"{speaker_name}:{msg}"
                if rendered not in self.recent_messages:
                    self.recent_messages.append(rendered)

                # Engine records the message
                self.public_chat_history.append((speaker_name, msg))
                events.append(ChatEvent(name_ia=speaker_name, text=msg, show_name_ia=True))

                # Add dialogue to global context in a readable format
                dialogue_context = {
                    "type": "dialogue",
                    "content": f"{speaker_name} dit: \"{msg}\""
                }
                self.context_manager.add_global_context(dialogue_context)

            except Exception as e:
                # Fallback message if OpenRouter fails
                fallback_msg = "..."
                events.append(ChatEvent(name_ia=speaker_name, text=fallback_msg, show_name_ia=True))
                print(f"[ERROR] Agent {speaker_name} failed to generate message: {e}")

        return events

    # Starts the day phase with discussion
    def start_day(self) -> List[ChatEvent]:
        self.phase = "JourDiscussion"

        # Add day start to context
        day_start_context = {
            "type": "phase_change",
            "content": f"Période: JourDiscussion. Début du Jour {self.day_count}."
        }
        self.context_manager.add_global_context(day_start_context)

        events = [ChatEvent("Système", f"Début du Jour {self.day_count}.", True)]
        events += self._generate_day_discussion(n_messages=8)
        return events

    # Starts the voting phase
    def start_vote(self) -> List[ChatEvent]:
        self.phase = "JourVote"

        # Add vote phase to context
        vote_context = {
            "type": "phase_change",
            "content": "Période: JourVote. La phase de vote commence. Les joueurs doivent élire quelqu'un à éliminer."
        }
        self.context_manager.add_global_context(vote_context)

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

        # Add elimination to context
        elimination_context = {
            "type": "elimination",
            "content": f"Le village a voté pour éliminer {target.name} (rôle: {target.role}). {target.name} est mort."
        }
        self.context_manager.add_global_context(elimination_context)

        # Passe à la nuit directement
        self.phase = "Nuit"

        # Add night phase to context
        night_context = {
            "type": "phase_change",
            "content": "Période: Nuit. La nuit tombe, les loups-garous vont agir."
        }
        self.context_manager.add_global_context(night_context)

        events.append(ChatEvent("???", "La nuit tombe…", False))
        events.append(ChatEvent("???", "…des pas dans l'ombre…", False))
        return events

    # Resolves the night and starts the next day
    def resolve_night_and_start_next_day(self) -> List[ChatEvent]:
        if self.phase != "Nuit":
            return []

        self._last_night_victim = None

        # Night : The wolves choose a victim using OpenRouter
        candidates = self.alive_villager_indexes()
        if candidates:
            # Use OpenRouter to let wolves decide on a victim
            alive_wolves = [p for p in self.players if p.alive and p.role == "loup"]
            if alive_wolves:
                wolf_agent = self.agents[alive_wolves[0].name]
                try:
                    night_play = wolf_agent.play("Nuit", self.client, self.context_manager)

                    # Find target by name
                    victim_index = None
                    if night_play.cible:
                        for i, player in enumerate(self.players):
                            if player.name == night_play.cible and player.alive and player.role != "loup":
                                victim_index = i
                                break

                    if victim_index is not None:
                        self.kill_player(victim_index)
                        self._last_night_victim = victim_index
                    else:
                        # Fallback to random selection
                        victim = self.rng.choice(candidates)
                        self.kill_player(victim)
                        self._last_night_victim = victim

                except Exception:
                    # Fallback to random selection if OpenRouter fails
                    victim = self.rng.choice(candidates)
                    self.kill_player(victim)
                    self._last_night_victim = victim
            else:
                # No wolves left, pick random victim
                victim = self.rng.choice(candidates)
                self.kill_player(victim)
                self._last_night_victim = victim

        # Next day
        self.day_count += 1

        events: List[ChatEvent] = []
        if self._last_night_victim is not None:
            victim_name = self.players[self._last_night_victim].name
            events.append(
                ChatEvent("Système", f"Au matin, on retrouve {victim_name} mort.", True)
            )

            # Add night death to context
            death_context = {
                "type": "night_death",
                "content": f"Au matin du jour {self.day_count}, {victim_name} a été trouvé mort, tué par les loups-garous pendant la nuit."
            }
            self.context_manager.add_global_context(death_context)
        else:
            events.append(ChatEvent("Système", "Au matin, personne n'est mort…", True))

            # Add no death to context
            no_death_context = {
                "type": "night_result",
                "content": f"Au matin du jour {self.day_count}, personne n'est mort pendant la nuit."
            }
            self.context_manager.add_global_context(no_death_context)

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

                # Add night phase to context
                night_context = {
                    "type": "phase_change",
                    "content": "Période: Nuit. La nuit tombe, les loups-garous vont agir."
                }
                self.context_manager.add_global_context(night_context)

                return [
                    ChatEvent("???", "La nuit tombe…", False),
                    ChatEvent("???", "…des pas dans l'ombre…", False),
                ]

        if self.phase == "Nuit":
            return self.resolve_night_and_start_next_day()

        # No action for other phases
        return []
