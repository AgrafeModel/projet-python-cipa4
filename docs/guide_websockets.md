# 🔌 Guide complet des WebSockets

## 📚 Table des matières

1. [Qu'est-ce qu'un WebSocket?](#quest-ce-quun-websocket)
2. [HTTP vs WebSocket](#http-vs-websocket)
3. [Comment ça marche?](#comment-ça-marche)
4. [Architecture dans notre projet](#architecture-dans-notre-projet)
5. [Exemples pratiques](#exemples-pratiques)
6. [Cas d'usage](#cas-dusage)
7. [Avantages et inconvénients](#avantages-et-inconvénients)

---

## Qu'est-ce qu'un WebSocket?

Un **WebSocket** est un protocole de communication bidirectionnel en temps réel entre un client et un serveur.

### Analogie simple 🎯

Imaginez la différence entre:

**HTTP classique = Courrier postal** 📬
- Vous envoyez une lettre (requête)
- Vous attendez la réponse
- Une nouvelle lettre = une nouvelle requête complète
- Chaque échange recommence de zéro

**WebSocket = Ligne téléphonique** ☎️
- Vous appelez une fois
- La ligne reste ouverte
- Vous pouvez parler et écouter en même temps
- Pas besoin de rappeler à chaque phrase
- Communication continue et instantanée

---

## HTTP vs WebSocket

### HTTP Traditionnel

```
Client                          Serveur
  |                                |
  |------ GET /data ------------->|
  |                                |
  |<----- 200 OK + data ----------|
  |                                |
  |------ GET /data ------------->|  (nouvelle connexion)
  |                                |
  |<----- 200 OK + data ----------|
  |                                |
```

**Caractéristiques:**
- ❌ Unidirectionnel (client → serveur)
- ❌ Une requête = une réponse
- ❌ Reconnexion à chaque fois
- ❌ Overhead important (headers HTTP répétés)
- ✅ Simple et stateless
- ✅ Parfait pour les pages web classiques

### WebSocket

```
Client                          Serveur
  |                                |
  |------ Handshake HTTP -------->|
  |<----- Upgrade to WS ----------|
  |====== Connexion ouverte ======|
  |                                |
  |<===== Message 1 ==============|
  |====== Message 2 =============>|
  |<===== Message 3 ==============|
  |====== Message 4 =============>|
  |                                |
  |====== Connexion ouverte ======|
```

**Caractéristiques:**
- ✅ Bidirectionnel (client ↔ serveur)
- ✅ Connexion persistante
- ✅ Temps réel
- ✅ Faible latence
- ✅ Moins d'overhead
- ❌ Plus complexe à gérer
- ❌ Nécessite un serveur compatible

---

## Comment ça marche?

### 1️⃣ Établissement de la connexion (Handshake)

Le client envoie une requête HTTP spéciale:

```http
GET /ws/client_123 HTTP/1.1
Host: localhost:8000
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

Le serveur répond:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

🎉 La connexion est maintenant **upgradée** en WebSocket!

### 2️⃣ Communication bidirectionnelle

Une fois connecté, **les deux parties** peuvent envoyer des messages à tout moment:

```
Client                          Serveur
  |                                |
  |------ "Bonjour" ------------->|
  |<----- "Salut!" ---------------|
  |                                |
  |<----- "Nouvelle notif!" ------|  (serveur → client)
  |                                |
  |------ "Message urgent" ------>|
  |<----- "Reçu!" ---------------|
```

### 3️⃣ Format des messages

Dans notre projet, nous utilisons **JSON**:

```json
{
  "message_type": "agent_message",
  "client_id": "agent_1",
  "timestamp": 1706580000.0,
  "agent_name": "Alice",
  "message_text": "Je pense que Bob est suspect!",
  "phase": "discussion"
}
```

### 4️⃣ Fermeture de la connexion

```python
# Fermeture propre
await websocket.close()

# Ou déconnexion inattendue détectée
try:
    await websocket.send(message)
except WebSocketDisconnect:
    # Client déconnecté
    cleanup()
```

---

## Architecture dans notre projet

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    Serveur WebSocket                     │
│                  (FastAPI + Uvicorn)                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         ConnectionManager                       │    │
│  │  • Gère toutes les connexions                  │    │
│  │  • Broadcast aux clients                       │    │
│  │  • Tracking par type (agent/ui/observer)       │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Message Schemas (Pydantic)             │    │
│  │  • Validation automatique                      │    │
│  │  • Types de messages définis                   │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
            ▲           ▲            ▲
            │           │            │
    WebSocket WS     WebSocket WS   WebSocket WS
            │           │            │
            ▼           ▼            ▼
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │  Agent  │  │  Agent   │  │    UI    │
    │   LLM   │  │   LLM    │  │  Client  │
    │ (Alice) │  │  (Bob)   │  │ (Pygame) │
    └─────────┘  └──────────┘  └──────────┘
```

### Flux de messages

#### Exemple 1: Agent envoie un message

```python
# 1. Agent Alice décide de parler
agent_alice.decide_message()

# 2. Envoie via WebSocket
message = {
    "message_type": "agent_message",
    "client_id": "agent_alice",
    "agent_name": "Alice",
    "message_text": "Je pense que Bob est le loup!"
}
await websocket.send(json.dumps(message))

# 3. Serveur reçoit et broadcast à tous les UI clients
await manager.broadcast(message, target_type="ui")

# 4. Interface Pygame reçoit et affiche
# ChatBox.add_message("Alice", "Je pense que Bob est le loup!")
```

#### Exemple 2: Broadcast d'état de jeu

```python
# 1. GameEngine change de phase
game_engine.current_phase = "night"

# 2. Crée un message d'état
state_message = {
    "message_type": "phase_update",
    "old_phase": "day",
    "new_phase": "night",
    "description": "La nuit tombe sur le village..."
}

# 3. Broadcast à TOUS les clients
await manager.broadcast(state_message)

# 4. Tous les clients (agents + UI) reçoivent
# - Agents: adaptent leur comportement
# - UI: met à jour l'affichage
```

---

## Exemples pratiques

### Côté Client (Python)

#### Connexion simple

```python
import asyncio
import websockets
import json

async def connect_to_server():
    uri = "ws://localhost:8000/ws/my_client_id?client_type=ui"
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connecté!")
        
        # Recevoir message de bienvenue
        welcome = await websocket.recv()
        print(f"Reçu: {welcome}")
        
        # Envoyer un message
        message = {
            "message_type": "ping",
            "client_id": "my_client_id",
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(message))
        
        # Recevoir réponse
        response = await websocket.recv()
        print(f"Réponse: {response}")

asyncio.run(connect_to_server())
```

#### Écouter en continu

```python
async def listen_forever():
    uri = "ws://localhost:8000/ws/listener?client_type=observer"
    
    async with websockets.connect(uri) as websocket:
        print("👂 En écoute...")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"📨 [{data['message_type']}] {data}")
        except websockets.ConnectionClosed:
            print("❌ Connexion fermée")
```

### Côté Serveur (FastAPI)

#### Endpoint WebSocket

```python
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    client_type: str = Query("ui")
):
    # Accepter la connexion
    await manager.connect(websocket, client_id, client_type)
    
    try:
        # Boucle d'écoute
        while True:
            # Recevoir message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Traiter le message
            await handle_message(client_id, message)
    
    except WebSocketDisconnect:
        # Nettoyer la déconnexion
        manager.disconnect(client_id)
```

#### Broadcast sélectif

```python
# Broadcast à tous
await manager.broadcast({"msg": "Pour tout le monde"})

# Broadcast aux agents seulement
await manager.broadcast(
    {"msg": "Pour les agents"},
    target_type="agent"
)

# Broadcast à tous SAUF un client
await manager.broadcast(
    {"msg": "Pour les autres"},
    exclude_client="agent_1"
)

# Message privé
await manager.send_personal(
    "agent_1",
    {"msg": "Message privé"}
)
```

---

## Cas d'usage

### Dans le jeu Loup-Garou

| Situation | Utilisation WebSocket | Bénéfice |
|-----------|----------------------|----------|
| **Agent parle** | Agent → Serveur → UI | Affichage temps réel dans chat |
| **Phase change** | GameEngine → Tous | Synchronisation instantanée |
| **Vote lancé** | GameEngine → Tous | UI update + agents notifiés |
| **Mort d'un joueur** | GameEngine → Tous | Broadcast événement important |
| **Action de nuit** | Agent loup → GameEngine | Action secrète transmise |
| **Observation** | Plusieurs UI connectées | Multi-spectateurs en temps réel |

### Avantages pour notre projet

✅ **Agents autonomes**
- Chaque agent LLM est un client WebSocket indépendant
- Peut communiquer sans bloquer les autres
- Décisions prises en parallèle

✅ **Interface réactive**
- L'interface Pygame reçoit les updates instantanément
- Pas de polling (vérification répétée)
- Fluidité de l'expérience utilisateur

✅ **Architecture distribuée**
- Serveur central orchestre le jeu
- Agents peuvent tourner sur différentes machines
- Interface séparée du moteur de jeu

✅ **Extensibilité**
- Facile d'ajouter des observateurs
- Support multi-interfaces (Pygame, web, mobile)
- Logs et monitoring en temps réel

---

## Patterns de communication

### 1. Request-Response (comme HTTP)

```python
# Client envoie une question
await websocket.send(json.dumps({
    "message_type": "query",
    "question": "Qui est vivant?"
}))

# Serveur répond
await websocket.send(json.dumps({
    "message_type": "response",
    "data": ["Alice", "Bob", "Charlie"]
}))
```

### 2. Pub-Sub (Publish-Subscribe)

```python
# Un client publie un événement
await manager.broadcast({
    "message_type": "event",
    "event": "player_died",
    "player_id": "alice"
})

# Tous les subscribers reçoivent
# - UI met à jour l'affichage
# - Agents mettent à jour leur mémoire
# - Logger enregistre l'événement
```

### 3. Heartbeat (Keep-Alive)

```python
# Serveur envoie des pings réguliers
async def heartbeat():
    while True:
        await asyncio.sleep(30)  # Toutes les 30s
        await websocket.send(json.dumps({
            "message_type": "ping"
        }))

# Client répond
if message["message_type"] == "ping":
    await websocket.send(json.dumps({
        "message_type": "pong"
    }))
```

---

## Avantages et inconvénients

### ✅ Avantages

| Avantage | Explication | Notre usage |
|----------|-------------|-------------|
| **Temps réel** | Latence minimale | Messages d'agents instantanés |
| **Bidirectionnel** | Serveur peut push | GameEngine notifie changements |
| **Efficace** | Connexion persistante | Moins d'overhead réseau |
| **Scalable** | Gestion multi-clients | Support de 8+ agents + UI |
| **Flexible** | Format libre (JSON) | Messages structurés avec Pydantic |

### ❌ Inconvénients

| Inconvénient | Impact | Notre solution |
|--------------|--------|----------------|
| **Complexité** | Plus dur à débugger | Tests unitaires complets |
| **État** | Gestion des connexions | ConnectionManager dédié |
| **Reconnexion** | Perte de connexion possible | Session tracking + retry |
| **Scalabilité** | Limite par serveur | Suffisant pour notre cas |
| **Sécurité** | Pas d'auth par défaut | À ajouter en production |

---

## Débogage et monitoring

### Voir les connexions actives

```bash
curl http://localhost:8000/stats
```

```json
{
  "total_clients": 5,
  "by_type": {
    "agent": 3,
    "ui": 2
  },
  "clients": [
    {"client_id": "agent_alice", "type": "agent"},
    {"client_id": "agent_bob", "type": "agent"},
    ...
  ]
}
```

### Logs du serveur

```
INFO:     127.0.0.1:54321 - "WebSocket /ws/agent_alice" [accepted]
✓ Client connected: agent_alice (type: agent)
INFO:     127.0.0.1:54322 - "WebSocket /ws/ui_main" [accepted]
✓ Client connected: ui_main (type: ui)
✗ Client disconnected: agent_alice
```

### Outils de test

- **Postman** - Support WebSocket intégré
- **wscat** - CLI pour WebSocket (`npm install -g wscat`)
- **Browser DevTools** - Console JavaScript
- **Notre script** - `python test_server.py`

---

## Ressources et références

### Documentation officielle

- 📖 [RFC 6455 - WebSocket Protocol](https://tools.ietf.org/html/rfc6455)
- 📖 [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- 📖 [Python websockets library](https://websockets.readthedocs.io/)
- 📖 [MDN WebSocket API](https://developer.mozilla.org/fr/docs/Web/API/WebSocket)

### Dans notre projet

- 📁 `server/websocket_server.py` - Implémentation serveur
- 📁 `server/connection_manager.py` - Gestion connexions
- 📁 `server/schemas.py` - Types de messages
- 📁 `examples/websocket_client_example.py` - Exemples clients
- 📁 `tests/test_websocket_server_simple.py` - Tests
- 📁 `server/README.md` - Documentation API

---

## Résumé en 30 secondes 🚀

**WebSocket = Ligne téléphonique permanente entre client et serveur**

✅ Bidirectionnel (↔)  
✅ Temps réel  
✅ Connexion persistante  
✅ Efficace pour jeux multi-agents  

**Notre usage:**
- Agents LLM → Serveur → Interface
- Communication temps réel
- Broadcast d'état de jeu
- Architecture distribuée

**Test rapide:**
```bash
# Terminal 1: Lancer le serveur
python start_server.py

# Terminal 2: Tester
python test_server.py
```

---

**Dernière mise à jour:** 30 janvier 2026  
**Version:** 1.0  
**Projet:** Loup-Garou Multi-Agents LLM
