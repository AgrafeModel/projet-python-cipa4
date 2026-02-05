#!/usr/bin/env python3
"""
Démonstration complète: Ollama LLM + WebSocket + Game Engine

Lance:
1. Un mini jeu avec agents LLM
2. Communique via WebSocket
3. Les agents parlent avec Ollama
"""

import asyncio
import json
from ai.agent_ollama import Agent, AgentConfig
from ai.rules import PublicState


def load_templates() -> dict:
    """Load templates."""
    try:
        with open("data/dialogue_ai_template.json", "r") as f:
            return json.load(f)
    except:
        return {
            "villageois": {"hedge": ["Je ne suis pas sûr..."]},
            "loup": {"hedge": ["Hmm, intéressant..."]},
            "common": {"connectors": [""], "softeners": [""], "endings": [""]}
        }


def main():
    """Simple game simulation with Ollama."""
    print("\n" + "=" * 70)
    print("🎮 Loup-Garou avec Ollama LLM - Démonstration")
    print("=" * 70)
    
    # Load templates
    templates = load_templates()
    
    # Create agents
    agents = [
        Agent(AgentConfig(name="Alice", role="villageois"), templates, seed=1),
        Agent(AgentConfig(name="Bob", role="loup"), templates, seed=2),
        Agent(AgentConfig(name="Charlie", role="villageois"), templates, seed=3),
        Agent(AgentConfig(name="Diana", role="villageois"), templates, seed=4),
    ]
    
    print(f"\n✅ {len(agents)} agents créés:")
    for agent in agents:
        status = "🤖 Ollama" if agent.use_ollama else "📝 Templates"
        print(f"   • {agent.name:8} ({agent.role:10}) - {status}")
    
    # Game state
    state = PublicState(
        alive_names=[a.name for a in agents],
        chat_history=[
            ("Narrateur", "Bienvenue à Loup-Garou! La première journée commence..."),
        ],
        day=1
    )
    
    print(f"\n🌍 État du jeu:")
    print(f"   • Jour: {state.day}")
    print(f"   • Vivants: {', '.join(state.alive_names)}")
    print(f"   • Messages: {len(state.chat_history)}")
    
    # Round 1: Day discussion
    print(f"\n{'='*70}")
    print(f"🗣️  JOUR {state.day} - Phase de discussion")
    print(f"{'='*70}\n")
    
    for agent in agents:
        print(f"💬 {agent.name}:", end=" ")
        
        # Observe state
        agent.observe_public(state)
        
        # Generate message
        message = agent.decide_message(state)
        print(f'"{message}"')
        
        # Add to chat
        state.chat_history.append((agent.name, message))
    
    # Round 2: Night (wolves kill)
    print(f"\n{'='*70}")
    print(f"🌙 NUIT {state.day} - Les loups-garous agissent")
    print(f"{'='*70}\n")
    
    wolves = [a for a in agents if a.role == "loup"]
    for wolf in wolves:
        victim = wolf.choose_night_victim(state.alive_names)
        print(f"🐺 {wolf.name} choisit de tuer: {victim}")
    
    # Results
    print(f"\n{'='*70}")
    print(f"📊 Résultats du jour {state.day}")
    print(f"{'='*70}\n")
    
    print(f"✅ Game simulation completed!")
    print(f"\nMessages générés par Ollama: {sum(1 for a in agents if a.use_ollama)}/{len(agents)}")
    
    print(f"\n{'='*70}")
    print(f"🚀 Prochaines étapes:")
    print(f"{'='*70}\n")
    print(f"1. Lancer le serveur WebSocket:")
    print(f"   python start_server.py\n")
    print(f"2. Lancer l'interface Pygame:")
    print(f"   python main.py\n")
    print(f"3. Voir les agents parler en temps réel via WebSocket!\n")


if __name__ == "__main__":
    main()
