#!/usr/bin/env python3
"""
Script de test pour le serveur WebSocket.
Lance des tests contre le serveur en cours d'exécution.
"""

import requests
import json
import time


def test_http_endpoints():
    """Teste les endpoints HTTP."""
    print("=" * 60)
    print("🧪 Test des endpoints HTTP")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n1️⃣ Test /health")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   📊 Connexions: {data['connections']}")
        else:
            print(f"   ❌ Erreur: Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur de connexion: {e}")
        print("   ⚠️  Le serveur est-il démarré?")
        return False
    
    # Test 2: Stats
    print("\n2️⃣ Test /stats")
    try:
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total clients: {data['total_clients']}")
            print(f"   📊 Par type: {data['by_type']}")
        else:
            print(f"   ❌ Erreur: Status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur: {e}")
    
    return True


def test_websocket_connection():
    """Teste une connexion WebSocket."""
    print("\n" + "=" * 60)
    print("🔌 Test de connexion WebSocket")
    print("=" * 60)
    
    try:
        import asyncio
        import websockets
        
        async def test_ws():
            uri = "ws://localhost:8000/ws/test_client_python?client_type=ui"
            print(f"\n📡 Connexion à {uri}...")
            
            try:
                async with websockets.connect(uri) as websocket:
                    print("   ✅ Connexion établie!")
                    
                    # Recevoir message de bienvenue
                    welcome = await websocket.recv()
                    print(f"   📨 Message de bienvenue reçu")
                    print(f"      {welcome[:100]}...")
                    
                    # Envoyer un ping
                    ping_msg = {
                        "message_type": "ping",
                        "client_id": "test_client_python",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(ping_msg))
                    print("   📤 Ping envoyé")
                    
                    # Recevoir pong
                    pong = await websocket.recv()
                    pong_data = json.loads(pong)
                    if pong_data.get("message_type") == "pong":
                        print("   📨 Pong reçu ✅")
                    
                    # Envoyer un message d'agent
                    agent_msg = {
                        "message_type": "agent_message",
                        "client_id": "test_client_python",
                        "timestamp": time.time(),
                        "agent_id": "agent_test",
                        "agent_name": "TestAgent",
                        "message_text": "Ceci est un message de test!",
                        "phase": "discussion"
                    }
                    await websocket.send(json.dumps(agent_msg))
                    print("   📤 Message d'agent envoyé ✅")
                    
                    print("\n   ✅ Tous les tests WebSocket réussis!")
                    
            except websockets.exceptions.ConnectionClosed:
                print("   ❌ Connexion fermée par le serveur")
            except Exception as e:
                print(f"   ❌ Erreur WebSocket: {e}")
        
        asyncio.run(test_ws())
        return True
        
    except ImportError:
        print("\n⚠️  Module 'websockets' non installé")
        print("   Installez-le avec: pip install websockets")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return False


def main():
    """Exécute tous les tests."""
    print("\n" + "=" * 60)
    print("🎮 Tests du serveur WebSocket Loup-Garou")
    print("=" * 60)
    print("\n⚠️  Assurez-vous que le serveur est démarré:")
    print("   python start_server.py")
    print()
    
    # Tests HTTP
    if not test_http_endpoints():
        print("\n❌ Tests échoués - Le serveur n'est pas accessible")
        return
    
    # Tests WebSocket
    test_websocket_connection()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés!")
    print("=" * 60)
    print("\nPour plus de tests, consultez:")
    print("  • examples/websocket_client_example.py")
    print("  • tests/test_websocket_server_simple.py")
    print()


if __name__ == "__main__":
    main()
