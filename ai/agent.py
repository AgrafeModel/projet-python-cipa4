# Fichier : ai/agent.py
# Gestion de l'agent IA (décisions, comportements, etc.)
# Note : Commentaires en anglais redigé par IA pour uniformité du code.
# Note : Certaines parties du code ont été générées par une IA (Copilot). Le code est fait à la
# main par l'humain, mais l'IA ajoute des optimisations et des suggestions.

from __future__ import annotations
import json
import random
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

from ai.rules import PublicState, choose_action_for_villager, choose_action_for_wolf, pick_target_weighted
from ai.ollama_client import OllamaClient
from config import load_ollama_config

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
        
        # Initialize Ollama client for LLM generation
        try:
            ollama_config = load_ollama_config()
            self.ollama_client = OllamaClient(ollama_config)
            self.ollama_model = ollama_config.model
            self.use_ollama = True
        except Exception as e:
            print(f"⚠️  Ollama not available for {self.name}: {e}")
            self.ollama_client = None
            self.use_ollama = False

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
        """Generate a message using Ollama LLM if available, fallback to templates."""
        candidates = [n for n in state.alive_names if n != self.name]
        if not candidates:
            return "…"

        # Try Ollama first
        if self.use_ollama and self.ollama_client:
            try:
                message = self._generate_with_ollama(state, candidates)
                if message:
                    return message
            except Exception as e:
                print(f"⚠️  Ollama generation failed for {self.name}: {e}")
                # Fall through to templates
        
        # Fallback to templates
        return self._generate_from_templates(candidates)
    
    def _generate_with_ollama(self, state: PublicState, candidates: List[str]) -> Optional[str]:
        """Generate message using Ollama LLM."""
        # Build context for the LLM (shorter for faster generation)
        recent_messages = "\n".join([f"{speaker}: {text}" for speaker, text in state.chat_history[-3:]])
        
        suspicion_info = "\n".join([
            f"- {name}: {sus:.1f}/5"
            for name, sus in sorted(self.suspicion.items(), key=lambda x: x[1], reverse=True)[:2]
        ])
        
        # Extract accusations against this player from recent messages
        accusations_against_me = []
        for speaker, text in state.chat_history[-3:]:
            if speaker != self.name and self.name.lower() in text.lower():
                if any(word in text.lower() for word in ["suspect", "louche", "cache", "bizarre", "suspecte", "loup", "mauvais"]):
                    accusations_against_me.append(f"{speaker}: {text}")
        
        accusations_text = "\n".join(accusations_against_me) if accusations_against_me else "(none)"
        
        # Build player list with roles (if available)
        role_map = getattr(state, 'role_map', {})
        player_list = ", ".join([f"{name} ({role_map.get(name, '?')})" for name in state.alive_names])
        
        prompt = f"""Tu es {self.name}, un joueur de Loup-Garou (Werewolf).
Ton rôle: {self.role}

Joueurs vivants: {player_list}

Messages récents:
{recent_messages}

Joueurs suspects:
{suspicion_info}

Accusations contre toi:
{accusations_text}

Écris UNE SEULE phrase en français (maximum 20 mots).
RÈGLES STRICTES:
- Réponds UNIQUEMENT EN FRANÇAIS
- PAS de traduction anglaise
- PAS de parenthèses
- PAS de guillemets
- Une seule phrase courte

Réponse:"""

        try:
            response = self.ollama_client.generate(
                prompt=prompt,
                model=self.ollama_model,
                options={"temperature": 0.5, "num_predict": 40}
            )
            
            if response and response.response:
                message = response.response.strip()
                
                # Remove any parenthetical content (often English translations)
                import re
                message = re.sub(r'\s*\([^)]*\)', '', message)
                
                # Clean up the message
                message = message.strip('"\'')
                if message.startswith('1.') or message.startswith('1)'):
                    message = message[2:].strip()
                
                # Take only first line
                message = message.split('\n')[0].strip()
                
                # Ensure reasonable length
                if len(message) > 150:
                    message = message[:150] + "..."
                
                # Reject if empty or English
                if not message or self._is_mostly_english(message):
                    return None
                
                return message
            
            return None
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return None
    
    def _is_mostly_english(self, text: str) -> bool:
        """Check if text is mostly English (basic heuristic)."""
        english_words = {"the", "a", "is", "are", "you", "they", "think", "suspect", "that", "but", "and", "or"}
        words = text.lower().split()
        english_count = sum(1 for w in words if w in english_words)
        return english_count > len(words) * 0.5 if words else False
    
    def _generate_from_templates(self, candidates: List[str]) -> str:
        """Generate message using template system (fallback)."""
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
