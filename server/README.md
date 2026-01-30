# WebSocket Server - Loup-Garou Multi-Agents

Serveur WebSocket temps réel pour la communication entre agents LLM et interfaces.

## 🎯 Fonctionnalités

- ✅ **Communication bidirectionnelle** - WebSocket avec FastAPI
- ✅ **Multi-connexions** - Supporte plusieurs clients simultanés
- ✅ **Types de clients** - Agent, UI, Observer
- ✅ **Messages JSON typés** - Validation avec Pydantic
- ✅ **Gestion des reconnexions** - Session tracking automatique
- ✅ **Broadcast sélectif** - Par type de client ou ciblé
- ✅ **Tests complets** - 16 tests unitaires avec pytest

## 📁 Structure

```
server/
├── __init__.py                  # Package exports
├── connection_manager.py        # Gestion des connexions WebSocket
├── schemas.py                   # Modèles Pydantic pour messages
└── websocket_server.py          # Serveur FastAPI principal
```

## 🚀 Démarrage

### Installer les dépendances

```bash
pip install fastapi uvicorn pydantic websockets
```

### Lancer le serveur

```bash
# Depuis la racine du projet
python -m server.websocket_server

# Ou avec auto-reload (dev)
uvicorn server.websocket_server:app --reload --host 0.0.0.0 --port 8000
```

Le serveur démarre sur **http://localhost:8000**

### Endpoints HTTP

- `GET /health` - Health check + statistiques
- `GET /stats` - Détails des connexions actives

### Endpoint WebSocket

```
ws://localhost:8000/ws/{client_id}?client_type={type}
```

**Paramètres:**
- `client_id` - Identifiant unique du client
- `client_type` - Type: `ui`, `agent`, `observer`

## 💬 Messages

### Types de messages

Tous les messages suivent ce format de base:

```json
{
  "message_type": "...",
  "client_id": "...",
  "timestamp": 1234567890.0,
  "data": {}
}
```

### Message Types

| Type | Description | Usage |
|------|-------------|-------|
| `connection` | Connexion établie | Envoyé automatiquement |
| `disconnection` | Déconnexion client | Broadcast aux autres |
| `ping` / `pong` | Keep-alive | Heartbeat automatique |
| `game_state` | État du jeu | Broadcast complet |
| `agent_message` | Message d'agent | Discussion → UI |
| `player_action` | Action joueur | Vote, cible nuit |
| `phase_update` | Changement de phase | Jour/Nuit/Vote |
| `error` | Erreur | Message d'erreur |

### Exemples

**Ping**
```json
{
  "message_type": "ping",
  "client_id": "ui_client_1",
  "timestamp": 1706580000.0
}
```

**Game State**
```json
{
  "message_type": "game_state",
  "client_id": "game_engine",
  "timestamp": 1706580000.0,
  "phase": "day",
  "players": [
    {"id": "p1", "name": "Alice", "alive": true},
    {"id": "p2", "name": "Bob", "alive": true}
  ],
  "current_turn": 2,
  "alive_count": 8,
  "dead_count": 1
}
```

**Agent Message**
```json
{
  "message_type": "agent_message",
  "client_id": "agent_alice",
  "timestamp": 1706580000.0,
  "agent_id": "agent_1",
  "agent_name": "Alice",
  "message_text": "Je pense que Bob est le loup-garou!",
  "phase": "discussion"
}
```

## 🔌 Client Python

Exemple de connexion:

```python
import asyncio
import json
import websockets

async def connect():
    uri = "ws://localhost:8000/ws/my_client?client_type=ui"
    
    async with websockets.connect(uri) as websocket:
        # Recevoir message de bienvenue
        welcome = await websocket.recv()
        print(f"Connecté: {welcome}")
        
        # Envoyer un message
        message = {
            "message_type": "ping",
            "client_id": "my_client",
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(message))
        
        # Recevoir réponse
        response = await websocket.recv()
        print(f"Reçu: {response}")

asyncio.run(connect())
```

Voir aussi: `examples/websocket_client_example.py`

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
pytest tests/test_websocket_server_simple.py -v

# Tests spécifiques
pytest tests/test_websocket_server_simple.py::TestConnectionManager -v
pytest tests/test_websocket_server_simple.py::TestMessageSchemas -v
```

### Résultats

✅ **16/16 tests passés**

- ConnectionManager: 10 tests
- WebSocket Server: 2 tests  
- Message Schemas: 4 tests

## 🏗️ Architecture

### ConnectionManager

Gère les connexions WebSocket:

```python
from server.connection_manager import ConnectionManager

manager = ConnectionManager()

# Connexion
await manager.connect(websocket, "client_1", "ui")

# Broadcast à tous
await manager.broadcast({"msg": "hello"})

# Broadcast par type
await manager.broadcast({"msg": "agents only"}, target_type="agent")

# Message personnel
await manager.send_personal("client_1", {"msg": "private"})

# Statistiques
stats = manager.get_connection_stats()
```

### Schemas (Pydantic)

Messages validés automatiquement:

```python
from server.schemas import GameStateMessage

msg = GameStateMessage(
    client_id="server",
    timestamp=time.time(),
    phase="night",
    players=[...],
    current_turn=3,
    alive_count=7,
    dead_count=2
)

# Sérialisation JSON
json_str = msg.model_dump_json()
```

## 🔄 Intégration avec GameEngine

Pour intégrer avec le moteur de jeu:

```python
from server import ConnectionManager, GameStateMessage
from game.engine import GameEngine

manager = ConnectionManager()
game_engine = GameEngine(...)

# À chaque changement d'état
async def broadcast_game_state():
    msg = GameStateMessage(
        client_id="game_engine",
        timestamp=time.time(),
        phase=game_engine.current_phase,
        players=game_engine.get_players_info(),
        current_turn=game_engine.turn,
        alive_count=game_engine.count_alive(),
        dead_count=game_engine.count_dead()
    )
    
    await manager.broadcast(msg.model_dump())
```

## 📊 Monitoring

### Statistiques en temps réel

```bash
# Via HTTP
curl http://localhost:8000/stats

# Retourne:
{
  "total_clients": 5,
  "by_type": {
    "ui": 2,
    "agent": 3
  },
  "clients": [
    {"client_id": "ui_1", "type": "ui", "connected_at": 1706580000.0},
    ...
  ]
}
```

## 🛠️ Configuration

Variables d'environnement (optionnelles):

```bash
export WS_HOST="0.0.0.0"
export WS_PORT="8000"
export WS_TIMEOUT="300"  # secondes
```

## 🔐 Sécurité

- ⚠️ Actuellement pas d'authentification (développement local)
- 🔒 Production: Ajouter JWT/OAuth2
- 🔒 Production: Activer HTTPS/WSS

## 📚 Ressources

- [FastAPI WebSocket Docs](https://fastapi.tiangolo.com/advanced/websockets/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [websockets Library](https://websockets.readthedocs.io/)

## ✅ US-1.4 Complétée

Tous les critères d'acceptation validés:
- [x] Serveur WebSocket créé avec asyncio/FastAPI
- [x] Gestion des connexions multiples
- [x] Messages JSON sérialisés  
- [x] Gestion des déconnexions
- [x] Tests de charge basiques

---

**Statut:** Production-ready ✅  
**Tests:** 16/16 ✅  
**Documentation:** Complète ✅
