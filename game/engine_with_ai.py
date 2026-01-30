# File: game/engine_with_gemini.py

from __future__ import annotations

import json
import random
import os
from dataclasses import dataclass
from typing import List, Optional
from collections import deque

from game.structure_ai import Player
import google.generativeai as genai

@dataclass
class ChatEvent:
    name_ia: str
    text: str
    show_name_ia: bool


class GeminiDialogueIntegration:

    def __init__(self, api_key: str):
        # API key configuration
        genai.configure(api_key='AIzaSyD2W1Dq4Px-7SuFu6d6lDwXK9wt_8WS9t8')  
        
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        self.generation_config = {
            'temperature': 0.9,  # Creativity
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 3000,
        }

    def _build_prompt(self, players: List[Player], day: int, 
                     eliminated: List[str], wolves_found: List[str], 
                     history: List[tuple]) -> str:
        """Construit le prompt pour générer toute la discussion du jour"""
        
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
            for speaker, text in history[-6:]:  # 6 derniers messages
                prompt += f"{speaker}: {text}\n"
        
        # Instructions for roles
        prompt += "\nRÔLES SECRETS (à respecter) :\n"
        for p in players:
            if p.alive:
                role_info = "LOUP (doit mentir et accuser des innocents)" if p.role == "loup" else "VILLAGEOIS (cherche les loups)"
                prompt += f"- {p.name} : {role_info}\n"
        
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
            print(f"⚠ Erreur Gemini: {e}")
            # Fallback
            return "La discussion IA ne peut pas être générée pour l'instant."


class GameEngine:

    def __init__(self, num_players: int, seed: Optional[int] = None, 
                 use_ai_dialogue: bool = True, gemini_api_key: Optional[str] = None):
        if num_players < 6:
            raise ValueError("num_players must be >= 6")

        self.rng = random.Random(seed)
        self.day_count = 1
        self.phase = "JourDiscussion"

        # Load players names
        with open("data/ai_names.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self.ai_names = data["prenoms"]

        self.players: List[Player] = self._create_players(num_players)
        self._last_night_victim: Optional[int] = None
        self.found_wolves_names: set[str] = set()
        self.public_chat_history: list[tuple[str, str]] = []

        self.use_ai_dialogue = use_ai_dialogue
        
        if use_ai_dialogue:
            if gemini_api_key is None:
                gemini_api_key = 'AIzaSyD2W1Dq4Px-7SuFu6d6lDwXK9wt_8WS9t8'
            
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

        self.recent_messages = deque(maxlen=40)

    def _create_players(self, num_players: int) -> List[Player]:
        names = self.rng.sample(self.ai_names, num_players)
        num_wolves = max(1, num_players // 4)
        roles = ["loup"] * num_wolves + ["villageois"] * (num_players - num_wolves)
        self.rng.shuffle(roles)
        return [Player(name=n, role=r, alive=True, note=0) for n, r in zip(names, roles)]

    def alive_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive]

    def alive_wolf_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive and p.role == "loup"]

    def alive_villager_indexes(self) -> List[int]:
        return [i for i, p in enumerate(self.players) if p.alive and p.role != "loup"]

    def all_wolves_names(self) -> list[str]:
        return [p.name for p in self.players if p.role == "loup"]

    def found_wolves_list(self) -> list[str]:
        return sorted(self.found_wolves_names)
    
    def get_winner(self) -> Optional[str]:
        wolves = len(self.alive_wolf_indexes())
        villagers = len(self.alive_villager_indexes())
        if wolves == 0:
            return "village"
        if wolves >= villagers:
            return "loups"
        return None

    def kill_player(self, index: int) -> None:
        p = self.players[index]
        p.alive = False
        p.note = 0

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
                    
                    if name not in [p.name for p in alive_players]:
                        continue
                    
                    events.append(ChatEvent(name_ia=name, text=text, show_name_ia=True))
                    self.public_chat_history.append((name, text))
                
                # Fallback
                if not events:
                    print("⚠ Aucun message valide généré, utilisation du fallback")
                    events = self._generate_simple([p.name for p in alive_players], n_messages=8)
                    
            except Exception as e:
                print(f"⚠ Erreur génération discussion: {e}")
                events = self._generate_simple([p.name for p in alive_players], n_messages=8)
        else:
            # Mode fallback
            events = self._generate_simple([p.name for p in alive_players], n_messages=8)

        return events

    def _generate_simple(self, alive_names: List[str], n_messages: int) -> list[ChatEvent]:
        """Génération simple sans IA (fallback)"""
        templates = [
            "Je trouve ça suspect.", 
            "On devrait observer plus attentivement.",
            "Je ne suis pas convaincu.", 
            "Quelqu'un cache quelque chose.",
            "Je reste prudent.", 
            "Ça me paraît louche.",
            "On manque d'infos.", 
            "Je pense qu'on devrait voter.",
            "Franchement, je ne sais pas trop.", 
            "Perso, j'ai des doutes."
        ]
        events = []
        for _ in range(n_messages):
            speaker = self.rng.choice(alive_names)
            msg = self.rng.choice(templates)
            self.public_chat_history.append((speaker, msg))
            events.append(ChatEvent(name_ia=speaker, text=msg, show_name_ia=True))
        return events

    def start_day(self) -> List[ChatEvent]:
        """Démarre un nouveau jour"""
        self.phase = "JourDiscussion"
        events = [ChatEvent("Système", f"Début du Jour {self.day_count}.", True)]
        events += self._generate_day_discussion()
        return events

    def start_vote(self) -> List[ChatEvent]:
        """Démarre la phase de vote"""
        self.phase = "JourVote"
        return [ChatEvent("Système", "Vote : clique sur le bouton bleu puis confirme.", True)]

    def cast_vote(self, target_index: int) -> List[ChatEvent]:
        """Élimine un joueur par vote"""
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

    def resolve_night_and_start_next_day(self) -> List[ChatEvent]:
        """Résout la nuit et commence le jour suivant"""
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

    def advance(self) -> List[ChatEvent]:
        """Avance la phase du jeu"""
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