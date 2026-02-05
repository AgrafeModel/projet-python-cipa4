# 🎮 Guide Complet: Tester Ollama + WebSocket + Agents

## 🎯 Objectif
Tester le système complet: Ollama génère du texte → Agents le parlent → WebSocket le communique → UI l'affiche

## 📋 Prérequis

### 1. Ollama en cours d'exécution
```bash
# Terminal 1: Lancer Ollama
ollama serve

# Vérifier dans un autre terminal
curl http://localhost:11434/api/tags
# Devrait montrer: {"models":[{"name":"mistral:latest",...}]}
```

### 2. Dépendances installées
```bash
# Venv activé
source .venv/bin/activate

# Packages installés
pip list | grep -E "fastapi|websocket|requests|pydantic"
```

### 3. Git prêt
```bash
# Sur la branche feature/ollama-integration
git branch
# Devrait afficher: * feature/ollama-integration

# Vérifier les fichiers modifiés
git status
```

---

## 🚀 Test 1: Agents avec Ollama

### Lancer la démo
```bash
python demo_ollama_game.py
```

### Résultat attendu
```
✅ 4 agents créés:
   • Alice    (villageois) - 🤖 Ollama
   • Bob      (loup      ) - 🤖 Ollama
   • Charlie  (villageois) - 🤖 Ollama
   • Diana    (villageois) - 🤖 Ollama

💬 Alice: "Je suis préoccupé par..."
💬 Bob: "Je pense que la nuit prochaine..."
...

Messages générés par Ollama: 4/4
```

✅ **SUCCESS**: Tous les agents parlent avec Ollama!

---

## 🚀 Test 2: WebSocket Server

### Terminal 2: Lancer le serveur
```bash
python start_server.py
```

### Résultat attendu
```
============================================================
🎮 Serveur WebSocket Loup-Garou Multi-Agents
============================================================
📡 Host: 0.0.0.0
🔌 Port: 8000
🔄 Auto-reload: Oui
============================================================

Endpoints:
  • WebSocket: ws://0.0.0.0:8000/ws/{client_id}
  • Health:    http://0.0.0.0:8000/health
  • Stats:     http://0.0.0.0:8000/stats

🚀 WebSocket server starting...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

✅ **SUCCESS**: Serveur WebSocket en cours!

---

## 🚀 Test 3: Tester WebSocket

### Terminal 3: Tests HTTP
```bash
# Health check
curl http://localhost:8000/health
# Devrait retourner JSON avec status: "ok"

# Stats
curl http://localhost:8000/stats
# Devrait retourner JSON avec connexions
```

### Test WebSocket complet
```bash
python test_server.py
```

### Résultat attendu
```
============================================================
🧪 Test des endpoints HTTP
============================================================

1️⃣ Test /health
   ✅ Status: ok
   📊 Connexions: {'total_connections': 0, 'by_type': {}}

2️⃣ Test /stats
   ✅ Total clients: 0
   📊 Par type: {}

============================================================
🔌 Test de connexion WebSocket
============================================================

📡 Connexion à ws://localhost:8000/ws/test_client_python?client_type=ui...
   ✅ Connexion établie!
   📨 Message de bienvenue reçu
   📤 Ping envoyé
   📨 Pong reçu ✅
   📤 Message d'agent envoyé ✅

   ✅ Tous les tests WebSocket réussis!
```

✅ **SUCCESS**: WebSocket fonctionne!

---

## 🚀 Test 4: Agents + WebSocket

### Créer un script de test intégré
Créez `test_ollama_websocket.py`:

```python
import asyncio
import json
import websockets
from ai.agent import Agent, AgentConfig
from ai.rules import PublicState
from ai.ollama_client import OllamaClient

async def test_agent_with_websocket():
    """Agent génère message et l'envoie via WebSocket."""
    
    # 1. Create agent
    config = AgentConfig(name="TestAgent", role="villageois")
    templates = {
        "villageois": {"hedge": ["Je vote..."]},
        "loup": {"hedge": ["Hmm..."]},
        "common": {"connectors": [""], "softeners": [""], "endings": [""]}
    }
    agent = Agent(config, templates)
    
    # 2. Create game state
    state = PublicState(
        alive_names=["TestAgent", "Other"],
        chat_history=[("Other", "Quelqu'un d'anormal?")],
        day=1
    )
    
    # 3. Generate message with Ollama
    agent.observe_public(state)
    message_text = agent.decide_message(state)
    print(f"Agent message: {message_text}")
    
    # 4. Send via WebSocket
    uri = "ws://localhost:8000/ws/test_agent?client_type=agent"
    async with websockets.connect(uri) as websocket:
        # Send message
        msg = {
            "message_type": "agent_message",
            "client_id": "test_agent",
            "timestamp": 1234567890,
            "agent_id": agent.name,
            "agent_name": agent.name,
            "message_text": message_text,
            "phase": "discussion"
        }
        await websocket.send(json.dumps(msg))
        print("✅ Message envoyé via WebSocket!")

if __name__ == "__main__":
    asyncio.run(test_agent_with_websocket())
```

Lancer:
```bash
python test_ollama_websocket.py
```

✅ **SUCCESS**: Agent parle et envoie via WebSocket!

---

## 🔄 Flux complet du système

```
┌─────────────────────────────────────────────────────────┐
│                 Agent (Ollama)                          │
│                                                         │
│  1. Lit état du jeu (PublicState)                      │
│  2. Build prompt pour Ollama                           │
│  3. Appelle OllamaClient.generate()                    │
│  4. Ollama retourne message en français                │
└─────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────┐
│            WebSocket Client (Agent)                     │
│                                                         │
│  1. Connecte au serveur (ws://localhost:8000)          │
│  2. Envoie message JSON typé                           │
│  3. Serveur reçoit et route                            │
└─────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────┐
│         WebSocket Server (FastAPI)                      │
│                                                         │
│  1. Reçoit message d'agent                             │
│  2. Valide schema (Pydantic)                           │
│  3. Broadcast à clients UI                             │
│  4. Store dans ConnectionManager                       │
└─────────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────────┐
│         WebSocket Clients (UI/Pygame)                   │
│                                                         │
│  1. Reçoivent le message                               │
│  2. Mettent à jour affichage chat                      │
│  3. Affichent: "Alice: <message Ollama>"               │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Checklist de test

### Test 1: Ollama Agent
- [ ] `python demo_ollama_game.py` lance sans erreur
- [ ] Les 4 agents affichent "🤖 Ollama" (pas "📝 Templates")
- [ ] Messages générés en français
- [ ] Pas d'erreur de connexion à Ollama
- [ ] Exécution rapide (< 10s total)

### Test 2: WebSocket Server
- [ ] `python start_server.py` démarre sans erreur
- [ ] Serveur écoute sur port 8000
- [ ] Logs montrent "INFO: Application startup complete"
- [ ] Pas de warnings (sauf FastAPI normaux)

### Test 3: WebSocket Client
- [ ] `python test_server.py` passe tous les tests
- [ ] Health check: 200 OK
- [ ] Stats endpoint: retourne JSON
- [ ] WebSocket connection: acceptée
- [ ] Messages envoyés et reçus

### Test 4: Intégration
- [ ] Agent génère message
- [ ] Message envoyé via WebSocket
- [ ] Message reçu par serveur
- [ ] Broadcast fonctionne
- [ ] Pas de latence excessive

---

## 🔧 Débogage

### Si Ollama ne répond pas
```python
# Tester connexion
from config import load_ollama_config
from ai.ollama_client import OllamaClient

config = load_ollama_config()
print(f"Config: {config}")
# BASE_URL doit être http://localhost:11434

client = OllamaClient(config)
models = client.list_models()
print(f"Available models: {models}")
# Devrait afficher ['mistral:latest']
```

### Si WebSocket ne répond pas
```bash
# Vérifier que le port est libre
lsof -i :8000

# Vérifier WebSocket
curl -i http://localhost:8000/health
# Devrait avoir code 200
```

### Logs détaillés
```python
# Dans test_server.py, ajouter:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🎯 Success Criteria

✅ **Tous les tests passent**
```
- demo_ollama_game.py: 4/4 agents avec Ollama
- test_agent_ollama.py: Tests OK, fallback OK
- test_server.py: HTTP endpoints OK, WebSocket OK
- test_ollama_websocket.py: Intégration OK
```

✅ **Performance acceptable**
```
- Message generation: < 5 secondes
- WebSocket latency: < 100ms
- Server handles 10+ connections
```

✅ **Code quality**
```
- Pas d'erreurs
- Fallback fonctionnel
- Error handling proper
- Logs informatifs
```

---

## 🚀 Prochaines étapes après tests

### 1. Merge sur main
```bash
git push origin feature/ollama-integration
# Créer PR sur GitHub
```

### 2. Intégrer dans main.py (Pygame)
```python
# Dans game loop:
agent.observe_public(game_state)
message = agent.decide_message(game_state)
# Envoyer via WebSocket
await send_to_websocket(message)
```

### 3. Connecter interface Pygame
```python
# Dans GUI:
async def on_websocket_message(msg):
    if msg["message_type"] == "agent_message":
        chat_box.add_message(
            msg["agent_name"],
            msg["message_text"]
        )
```

---

## 📚 Documentation de référence

- 📖 [Guide WebSockets](docs/guide_websockets.md)
- 📖 [Feature Ollama Integration](docs/FEATURE_OLLAMA_INTEGRATION.md)
- 📖 [README serveur](server/README.md)
- 🧪 [Tests](tests/test_websocket_server_simple.py)

---

**Prêt à tester!** 🚀
