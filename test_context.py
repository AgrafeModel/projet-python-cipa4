#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour vérifier le fonctionnement du contexte dans le jeu Loup-Garou
"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.engine_openrouter import GameEngine
from ai.client import OpenRouterClient, OpenRouterClientConfig

def test_context():
    """Test le fonctionnement du contexte"""

    # Charger les variables d'environnement
    load_dotenv()

    print("=== Test du Context Manager ===\n")

    try:
        # Créer une partie de test avec 6 joueurs
        engine = GameEngine(num_players=6, seed=42)
        print(f"✓ Partie créée avec {len(engine.players)} joueurs")

        # Afficher les joueurs et leurs rôles (pour debug)
        print("\nJoueurs et rôles:")
        for i, player in enumerate(engine.players):
            print(f"  {i}: {player.name} - {player.role} ({'vivant' if player.alive else 'mort'})")

        print("\n=== Test du contexte initial ===")

        # Tester le contexte pour chaque joueur
        for player in engine.players[:2]:  # Test sur les 2 premiers joueurs seulement
            print(f"\n--- Contexte pour {player.name} (rôle: {player.role}) ---")
            context = engine.context_manager.get_full_global_player_context(player.name)
            print(f"Longueur du contexte: {len(context)} caractères")
            print("Contexte:")
            print(context)
            print("-" * 50)

        print("\n=== Test d'une action d'agent ===")

        # Simuler une action d'agent
        first_player = engine.players[0]
        agent = engine.agents[first_player.name]

        print(f"Agent {first_player.name} va jouer...")

        # Simuler une réponse d'agent (sans appeler l'API)
        from ai.client import ResponseFormat
        test_response = ResponseFormat(
            action="discuter",
            reasoning="Je dois observer les autres joueurs pour identifier les suspects",
            dialogue="Bonjour tout le monde ! Qui a des informations à partager ?",
            cible=""
        )

        # Ajouter manuellement au contexte comme le ferait l'agent
        global_context_content = {
            "type": "player_action",
            "content": f"{first_player.name} fait l'action '{test_response.action}' et dit: \"{test_response.dialogue}\""
        }
        engine.context_manager.add_global_context(global_context_content)

        player_context_content = {
            "type": "reasoning",
            "content": f"Mon raisonnement: {test_response.reasoning}"
        }
        engine.context_manager.add_player_context(first_player.name, player_context_content)

        print("✓ Action ajoutée au contexte")

        print("\n=== Contexte après action ===")

        # Vérifier le contexte après l'action
        for player in engine.players[:2]:
            print(f"\n--- Contexte mis à jour pour {player.name} ---")
            context = engine.context_manager.get_full_global_player_context(player.name)
            print(f"Longueur du contexte: {len(context)} caractères")
            print("Contexte:")
            print(context)
            print("-" * 50)

        print("\n=== Test du contexte global ===")
        global_context = engine.context_manager.get_global_context()
        print(f"Contexte global ({len(global_context)} caractères):")
        print(global_context)

        print("\n✓ Test du contexte terminé avec succès!")

    except Exception as e:
        print(f"✗ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_context()
