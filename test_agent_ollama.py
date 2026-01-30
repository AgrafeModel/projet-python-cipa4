#!/usr/bin/env python3
"""
Test Ollama LLM integration with Agent class.
Tests both Ollama generation and template fallback.

Requirements: Ollama running with 'mistral' model
"""

import asyncio
import json
from ai.agent import Agent, AgentConfig
from ai.rules import PublicState


def load_test_templates() -> dict:
    """Load templates for testing."""
    try:
        with open("data/dialogue_ai_template.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  Templates not found, using minimal fallback")
        return {
            "villageois": {"hedge": ["Je ne suis pas sûr..."]},
            "loup": {"hedge": ["Hmm, intéressant..."]},
            "common": {"connectors": [""], "softeners": [""], "endings": [""]}
        }


def test_ollama_generation():
    """Test Agent with Ollama generation."""
    print("=" * 60)
    print("🧪 Test: Agent with Ollama LLM Integration")
    print("=" * 60)
    
    # Load templates
    templates = load_test_templates()
    
    # Create agents
    alice_config = AgentConfig(name="Alice", role="villageois")
    bob_config = AgentConfig(name="Bob", role="loup")
    
    alice = Agent(alice_config, templates, seed=42)
    bob = Agent(bob_config, templates, seed=43)
    
    print(f"\n✅ Created agents:")
    print(f"   • Alice: {alice.role} (Ollama: {alice.use_ollama})")
    print(f"   • Bob: {bob.role} (Ollama: {bob.use_ollama})")
    
    # Create game state
    state = PublicState(
        alive_names=["Alice", "Bob", "Charlie", "Diana"],
        chat_history=[
            ("Alice", "Bonjour tout le monde!"),
            ("Bob", "Salut les gars"),
            ("Charlie", "Qui me soupçonne?"),
            ("Diana", "Je vois quelque chose de louche...")
        ],
        day=1
    )
    
    # Observe and generate messages
    print(f"\n📊 Game State:")
    print(f"   • Alive: {', '.join(state.alive_names)}")
    print(f"   • Day: {state.day}")
    print(f"   • Recent messages: {len(state.chat_history)}")
    
    print(f"\n💬 Testing message generation:")
    
    # Alice's message
    alice.observe_public(state)
    alice_msg = alice.decide_message(state)
    print(f"\n   Alice ({alice.role}):")
    print(f"   '{alice_msg}'")
    print(f"   • Ollama: {alice.use_ollama}")
    
    # Bob's message
    bob.observe_public(state)
    bob_msg = bob.decide_message(state)
    print(f"\n   Bob ({bob.role}):")
    print(f"   '{bob_msg}'")
    print(f"   • Ollama: {bob.use_ollama}")
    
    # Test multiple generations (should vary with Ollama)
    print(f"\n🔄 Testing variation in messages (3 generations):")
    for i in range(3):
        msg = alice.decide_message(state)
        print(f"   {i+1}. '{msg}'")
    
    print(f"\n✅ Test completed!")
    print("=" * 60)


def test_template_fallback():
    """Test fallback to templates when Ollama is not available."""
    print("\n" + "=" * 60)
    print("🧪 Test: Template Fallback (Ollama disabled)")
    print("=" * 60)
    
    templates = load_test_templates()
    config = AgentConfig(name="TestAgent", role="villageois")
    agent = Agent(config, templates, seed=42)
    
    # Force disable Ollama
    agent.use_ollama = False
    
    state = PublicState(
        alive_names=["TestAgent", "Other1", "Other2"],
        chat_history=[("Other1", "Suspect someone!"), ("Other2", "I agree!")],
        day=1
    )
    
    agent.observe_public(state)
    msg = agent.decide_message(state)
    
    print(f"\n✅ Generated message (templates only):")
    print(f"   '{msg}'")
    print(f"=" * 60)


def test_night_action():
    """Test night victim selection."""
    print("\n" + "=" * 60)
    print("🧪 Test: Night Victim Selection")
    print("=" * 60)
    
    templates = load_test_templates()
    config = AgentConfig(name="Wolf", role="loup")
    wolf = Agent(config, templates, seed=42)
    
    alive_players = ["Wolf", "Victim1", "Victim2", "Victim3"]
    
    print(f"\n🌙 Wolf selecting victims (5 choices):")
    victims = []
    for i in range(5):
        victim = wolf.choose_night_victim(alive_players)
        victims.append(victim)
        print(f"   {i+1}. {victim}")
    
    print(f"\n✅ Night action test completed!")
    print("=" * 60)


def main():
    """Run all tests."""
    print("\n")
    print("🎮 Loup-Garou Agent - Ollama Integration Tests")
    print("=" * 60)
    print("\nMake sure:")
    print("  1. Ollama is running (ollama serve)")
    print("  2. Mistral model is installed (ollama pull mistral)")
    print("=" * 60)
    
    test_ollama_generation()
    test_template_fallback()
    test_night_action()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  • Check the messages generated above")
    print("  • Commit changes: git add -A && git commit -m 'feat: integrate Ollama LLM'")
    print("  • Push: git push origin feature/ollama-integration")
    print()


if __name__ == "__main__":
    main()
