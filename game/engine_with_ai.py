# File: game/engine_with_gemini.py

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import List, Optional
from collections import deque
import game.constants
from game.structure_ai import Player
import google.generativeai as genai

# TTS
from game.tts_helper import speak_text
import audio_config

# Custom exception for API unavailability
class ApiUnavailableError(RuntimeError):
    pass

# Represents a single chat message event displayed to the user
@dataclass
class ChatEvent:
    name_ia: str            # Name of the player speaking
    text: str               # Message content
    show_name_ia: bool      # Whether the name should be visible (night mode)


class GeminiDialogueIntegration:

    def __init__(self, api_key: str):
        # API key configuration
        genai.configure(api_key=game.constants.API_GEMINI)  
        
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Generation parameters controlling creativity and length
        self.generation_config = {
            'temperature': 0.9,  # Creativity
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 3000,
        }

        # Builds a structured prompt for Gemini containing:
        # - Current game state
        # - Alive players
        # - Known information
        # - Recent chat history
        # - Role-based behavior instructions
    def _build_prompt(self, players: List[Player], day: int, 
                     eliminated: List[str], wolves_found: List[str], 
                     history: List[tuple]) -> str:
        
        alive_names = [p.name for p in players if p.alive]
        
        # Context
        prompt = f"""Tu es le narrateur d'une partie de Loup-Garou. Génère une discussion naturelle pour le Jour {day}.

CONTEXTE :
- Joueurs vivants : {', '.join(alive_names)}
"""
        
        if eliminated:
            prompt += f"- Joueurs éliminés : {', '.join(eliminated)}\n"
        if wolves_found:
            prompt += f"- Loups confirmés : {', '.join(wolves_found)}\n"
        
        # Add history to the prompt
        if history and len(history) > 0:
            prompt += "\nHISTORIQUE RÉCENT :\n"
            for speaker, text in history[-6:]:  # Last 6 messages
                prompt += f"{speaker}: {text}\n"
        
        # Wolves instructions
        prompt += "\nRÔLES SECRETS (à respecter) :\n"
        for p in players:
            if p.alive:
                role_info = "LOUP (doit mentir et accuser des innocents)" if p.role == "loup" else "VILLAGEOIS (cherche les loups)"
                prompt += f"- {p.name} : {role_info}\n"
        
        # Global generation rules
        prompt += """
INSTRUCTIONS :
1. Génère 8-10 messages de discussion
2. Chaque joueur parle 1-2 fois maximum
3. Format STRICT : "Nom: texte du message" (une ligne par message)
4. Messages courts (1-2 phrases max)
5. Style oral et naturel : "Franchement,", "Perso,", "Honnêtement,"
6. Les joueurs réagissent entre eux (questions, défenses, accusations)
7. Les loups accusent des innocents de manière crédible
8. Les villageois cherchent des incohérences
9. JAMAIS révéler le rôle directement

EXEMPLE DE FORMAT :
Marc: Franchement, je trouve Sophie suspecte.
Sophie: Marc, tu dis ça depuis hier sans aucune preuve.
Luc: Perso, je pense que Marc a un point. Sophie évite les questions.

GÉNÈRE LA DISCUSSION (format exact "Nom: texte") :
"""
        
        return prompt

    def generate_discussion(self, players: List[Player], day: int,
                          eliminated: List[str], wolves_found: List[str],
                          history: List[tuple]) -> str:
        
        prompt = self._build_prompt(players, day, eliminated, wolves_found, history)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise ApiUnavailableError(f"OpenRouter: {e}") from e


# Core game engine managing:
# - Game phases
# - Player states
# - Voting
# - Night/day transitions
# - AI or fallback discussions
class GameEngine:

    def __init__(self, num_players: int, seed: Optional[int] = None, 
                 use_ai_dialogue: bool = True, gemini_api_key: Optional[str] = None):
        if num_players < 6:
            raise ValueError("num_players must be >= 6")

        self.rng = random.Random(seed)
        self.day_count = 1
        self.phase = "JourDiscussion"
        self.supports_streaming_discussion = False

        # Load AI player names from JSON
        with open("data/ai_names.json", "r", encoding="utf-8") as f:
            self.characters_data = json.load(f)["characters"]

        # Initialize players and game state
        self.players: List[Player] = self._create_players(num_players)
        self._last_night_victim: Optional[int] = None
        self.found_wolves_names: set[str] = set()
        self.public_chat_history: list[tuple[str, str]] = []

        # Initialize Gemini if enabled
        self.use_ai_dialogue = use_ai_dialogue
        
        if use_ai_dialogue:
            if gemini_api_key is None:
                gemini_api_key = game.constants.API_GEMINI
            
            if gemini_api_key:
                try:
                    self.ai_dialogue = GeminiDialogueIntegration(gemini_api_key)
                    print("✓ Gemini initialisé avec succès")
                except Exception as e:
                    print(f"⚠ Erreur initialisation Gemini: {e}")
                    print("  → Utilisation du mode fallback")
                    self.use_ai_dialogue = False
            else:
                print("⚠ Pas de clé API Gemini fournie")
                print("  → Utilisation du mode fallback")
                self.use_ai_dialogue = False

        # Keep a rolling buffer of recent messages
        self.recent_messages = deque(maxlen=40)

    # Randomly assigns names and roles to players.
    # About 1/4 of players are wolves.
    def _create_players(self, num_players: int) -> List[Player]:
        # Choisir num_players personnages au hasard
        selected_chars = self.rng.sample(self.characters_data, num_players)
        
        num_wolves = max(1, num_players // 4)
        roles = ["loup"] * num_wolves + ["villageois"] * (num_players - num_wolves)
        self.rng.shuffle(roles)

        # Créer Player avec name, role et voice_id
        return [
            Player(
                name=char["name"],
                role=r,
                alive=True,
                note=0,
                voice_id=char["voice_id"]  # <-- ajout ici
            )
            for char, r in zip(selected_chars, roles)
        ]

    # Utility methods for querying alive players
    def alive_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive]

    # Utility methods for querying alive wolves and villagers
    def alive_wolf_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive and p.role == "loup"]

    # Utility method to get alive villagers (non-wolves)
    def alive_villager_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive and p.role != "loup"]
    
    # Utility method to get the names of all wolves (alive or not)
    def all_wolves_names(self) -> list[str]:
        return [p.name for p in self.players if p.role == "loup"]

    # Utility method to get the names of found wolves (those that have been identified by the village)
    def found_wolves_list(self) -> list[str]:
        return sorted(self.found_wolves_names)
    
    # Checks if the game has a winner and returns "village", "loups", or None if the game is still ongoing.
    def get_winner(self) -> Optional[str]:
        wolves = len(self.alive_wolf_indexes())
        villagers = len(self.alive_villager_indexes())
        if wolves == 0:
            return "village"
        if wolves >= villagers:
            return "loups"
        return None

    # Eliminates a player by index, marking them as dead and resetting their note.
    def kill_player(self, index: int) -> None:
        p = self.players[index]
        p.alive = False
        p.note = 0

    # Generates a discussion for the day using either the AI or a simple fallback method. The discussion is based on the current game state, including alive players, eliminated players, known wolves, and recent chat history. If AI generation fails, it falls back to a simple random discussion.
    def _generate_day_discussion(self) -> list[ChatEvent]:
        alive_players = [p for p in self.players if p.alive]
        eliminated = [p.name for p in self.players if not p.alive]
        wolves_found = list(self.found_wolves_names)
        events: list[ChatEvent] = []

        if self.use_ai_dialogue:
            try:
                discussion_text = self.ai_dialogue.generate_discussion(
                    alive_players, 
                    self.day_count, 
                    eliminated, 
                    wolves_found,
                    self.public_chat_history
                )

                # Split text line by line
                for line in discussion_text.split("\n"):
                    line = line.strip()
                    
                    if not line or ":" not in line:
                        continue
                    
                    parts = line.split(":", 1)
                    if len(parts) != 2:
                        continue
                    
                    name = parts[0].strip()
                    text = parts[1].strip()
                    
                    # Check if the speaker is an alive player
                    speaker_player = next((p for p in alive_players if p.name == name), None)
                    if not speaker_player:
                        continue
                    
                    # Add the message to events and public history
                    events.append(ChatEvent(name_ia=name, text=text, show_name_ia=True))
                    self.public_chat_history.append((name, text))
                
                if not events:
                    events = self._generate_simple([p.name for p in alive_players], n_messages=8)
                    
            except Exception as e:
                raise ApiUnavailableError(f"OpenRouter: {e}") from e

        return events

    # Start the day phase with discussion, returning a list of chat events to display to the user. This method sets the game phase to "JourDiscussion", generates the discussion using the AI or fallback method, and returns the resulting chat events.
    def start_day(self) -> List[ChatEvent]:
        self.phase = "JourDiscussion"
        events = [ChatEvent("Système", f"Début du Jour {self.day_count}.", True)]
        events += self._generate_day_discussion()
        return events

    # Starts the voting phase, returning a chat event with instructions for voting. This method sets the game phase to "JourVote" and returns a message instructing players to click the "Voter" button and confirm their vote.
    def start_vote(self) -> List[ChatEvent]:
        self.phase = "JourVote"
        return [ChatEvent("Système", "Vote : clique sur le bouton \"Voter\" puis confirme.", True)]

    # Handles a vote to eliminate a player by index. This method checks if the current phase is "JourVote", validates the target index, eliminates the targeted player, updates the found wolves if necessary, and returns chat events describing the elimination and transitioning to night.
    def cast_vote(self, target_index: int) -> List[ChatEvent]:
        if self.phase != "JourVote":
            return []
        if target_index < 0 or target_index >= len(self.players):
            return []
        if not self.players[target_index].alive:
            return []

        self.kill_player(target_index)
        target = self.players[target_index]
        
        if target.role == "loup":
            self.found_wolves_names.add(target.name)

        events = [ChatEvent("Système", f"Le village élimine {target.name}.", True)]
        self.phase = "Nuit"
        events.append(ChatEvent("???", "La nuit tombe…", False))
        return events

    # Resolves the night phase by randomly selecting a victim from the alive villagers, eliminating them, and then starting the next day. This method checks if the current phase is "Nuit", selects a victim from the alive villagers, eliminates them, increments the day count, and returns chat events describing the outcome of the night and starting the next day.
    def resolve_night_and_start_next_day(self) -> List[ChatEvent]:
        if self.phase != "Nuit":
            return []

        self._last_night_victim = None
        candidates = self.alive_villager_indexes()
        
        if candidates:
            victim = self.rng.choice(candidates)
            self.kill_player(victim)
            self._last_night_victim = victim

        self.day_count += 1
        events = []
        
        if self._last_night_victim is not None:
            name = self.players[self._last_night_victim].name
            events.append(ChatEvent("Système", f"Au matin, on retrouve {name} mort.", True))
        else:
            events.append(ChatEvent("Système", "Au matin, personne n'est mort…", True))

        events += self.start_day()
        return events

    # Advances the game by one step based on the current phase. If the phase is "JourDiscussion", it either starts the vote if it's the second day or transitions to night. If the phase is "Nuit", it resolves the night and starts the next day. This method returns a list of chat events describing the changes in game state and any messages to display to the user.
    def advance(self) -> List[ChatEvent]:
        if self.phase == "JourDiscussion":
            if self.day_count >= 2:
                return self.start_vote()
            else:
                self.phase = "Nuit"
                return [
                    ChatEvent("???", "La nuit tombe…", False),
                    ChatEvent("???", "…des pas dans l'ombre…", False)
                ]
        
        if self.phase == "Nuit":
            return self.resolve_night_and_start_next_day()
        
        return []