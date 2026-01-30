"""
FastAPI WebSocket server for Loup-Garou game.
Handles real-time communication between agents and UI clients.
Supports multiple concurrent connections with automatic reconnection.
"""

import json
import asyncio
import time
from typing import Dict
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from server.connection_manager import ConnectionManager
from server.schemas import (
    BaseMessage,
    ConnectionMessage,
    GameStateMessage,
    ErrorMessage,
    PingMessage,
    PongMessage,
    MessageType,
)


# Global connection manager
manager = ConnectionManager()

# Session tracking for reconnection support
client_sessions: Dict[str, Dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    print("🚀 WebSocket server starting...")
    yield
    # Shutdown
    print("🛑 WebSocket server shutting down...")
    # Close all connections
    for client_id in list(manager.active_connections.keys()):
        manager.disconnect(client_id)


app = FastAPI(
    title="Loup-Garou WebSocket Server",
    description="Real-time multi-agent game server",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": time.time(),
        "connections": manager.get_connection_stats()
    }


@app.get("/stats")
async def get_stats():
    """Get connection statistics."""
    return {
        "total_clients": len(manager.active_connections),
        "by_type": manager.get_connection_stats()["by_type"],
        "clients": [
            {
                "client_id": cid,
                "type": manager.client_metadata[cid]["type"],
                "connected_at": manager.client_metadata[cid]["connected_at"]
            }
            for cid in manager.get_connected_clients()
        ]
    }


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    client_type: str = Query("ui", description="Type of client: ui, agent, observer")
):
    """
    WebSocket endpoint for bidirectional communication.
    
    Parameters:
        client_id: Unique identifier for the client
        client_type: Type of client ("ui", "agent", "observer")
    
    Connection format: ws://localhost:8000/ws/{client_id}?client_type={type}
    """
    
    # Store session for reconnection
    if client_id not in client_sessions:
        client_sessions[client_id] = {
            "created_at": time.time(),
            "reconnect_count": 0,
            "last_message": None
        }
    
    try:
        # Accept connection
        await manager.connect(websocket, client_id, client_type)
        client_sessions[client_id]["reconnect_count"] += 1
        
        # Notify all clients of new connection
        connection_msg = ConnectionMessage(
            client_id=client_id,
            client_type=client_type,
            timestamp=time.time(),
            data={"joined": True, "total_clients": len(manager.active_connections)}
        )
        await manager.broadcast(
            json.loads(connection_msg.model_dump_json()),
            exclude_client=client_id
        )
        
        # Send welcome message to new client
        await manager.send_personal(
            client_id,
            {
                "message_type": "connection",
                "status": "connected",
                "client_id": client_id,
                "timestamp": time.time(),
                "data": {"message": f"Welcome {client_id}"}
            }
        )
        
        # Main message loop
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=300.0  # 5 minute timeout
                )
                
                message = json.loads(data)
                client_sessions[client_id]["last_message"] = time.time()
                
                # Route message based on type
                await handle_message(client_id, message)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                ping_msg = PingMessage(
                    client_id="server",
                    timestamp=time.time()
                )
                await manager.send_personal(
                    client_id,
                    json.loads(ping_msg.model_dump_json())
                )
            
            except json.JSONDecodeError:
                error_msg = ErrorMessage(
                    client_id="server",
                    timestamp=time.time(),
                    error_code="INVALID_JSON",
                    error_text="Message is not valid JSON"
                )
                await manager.send_personal(
                    client_id,
                    json.loads(error_msg.model_dump_json())
                )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        
        # Notify remaining clients
        disconnect_data = {
            "message_type": "disconnection",
            "client_id": client_id,
            "timestamp": time.time(),
            "data": {
                "disconnected": client_id,
                "remaining_clients": len(manager.active_connections)
            }
        }
        await manager.broadcast(disconnect_data)
    
    except Exception as e:
        manager.disconnect(client_id)
        print(f"Error in WebSocket handler: {e}")


async def handle_message(client_id: str, message: Dict):
    """
    Route message to appropriate handler based on message_type.
    """
    message_type = message.get("message_type")
    
    if message_type == MessageType.PING.value:
        # Respond to ping with pong
        pong_msg = PongMessage(
            client_id="server",
            timestamp=time.time()
        )
        await manager.send_personal(
            client_id,
            json.loads(pong_msg.model_dump_json())
        )
    
    elif message_type == MessageType.AGENT_MESSAGE.value:
        # Broadcast agent message to all UI clients
        message["timestamp"] = time.time()
        await manager.broadcast(message, target_type="ui")
    
    elif message_type == MessageType.GAME_STATE.value:
        # Broadcast game state (typically from game engine)
        message["timestamp"] = time.time()
        await manager.broadcast(message, exclude_client=client_id)
    
    elif message_type == MessageType.PLAYER_ACTION.value:
        # Route player action to game engine (agent that manages state)
        message["timestamp"] = time.time()
        # Could forward to a specific agent/engine client
        await manager.broadcast(message, target_type="agent")
    
    elif message_type == MessageType.PHASE_UPDATE.value:
        # Broadcast phase change to all clients
        message["timestamp"] = time.time()
        await manager.broadcast(message)
    
    else:
        # Echo unknown messages back (useful for testing)
        message["timestamp"] = time.time()
        message["echoed"] = True
        await manager.send_personal(client_id, message)


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Start the WebSocket server.
    
    Args:
        host: Server host (default: 0.0.0.0)
        port: Server port (default: 8000)
        reload: Enable auto-reload on code changes (development mode)
    """
    uvicorn.run(
        "server.websocket_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # Run: python -m server.websocket_server
    run_server(reload=True)
