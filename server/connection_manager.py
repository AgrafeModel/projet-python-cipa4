"""
Manages WebSocket connections for the game server.
Handles client connection/disconnection and message broadcasting.
"""

import json
import asyncio
from typing import Dict, List, Set
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages multiple WebSocket connections and enables broadcasting.
    Maintains a registry of active connections by client type.
    """
    
    def __init__(self):
        # Maps client_id -> WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # Maps client_type -> set of client_ids (e.g., "agent" -> {"agent_1", "agent_2"})
        self.connections_by_type: Dict[str, Set[str]] = {}
        # Maps client_id -> client_type and metadata
        self.client_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, client_type: str = "ui"):
        """Register a new connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        if client_type not in self.connections_by_type:
            self.connections_by_type[client_type] = set()
        self.connections_by_type[client_type].add(client_id)
        
        self.client_metadata[client_id] = {
            "type": client_type,
            "connected_at": asyncio.get_event_loop().time()
        }
        print(f"✓ Client connected: {client_id} (type: {client_type})")
    
    def disconnect(self, client_id: str):
        """Unregister a disconnected client."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            
            if client_id in self.client_metadata:
                client_type = self.client_metadata[client_id]["type"]
                if client_type in self.connections_by_type:
                    self.connections_by_type[client_type].discard(client_id)
                del self.client_metadata[client_id]
            
            print(f"✗ Client disconnected: {client_id}")
    
    async def broadcast(self, message: Dict, exclude_client: str = None, target_type: str = None):
        """
        Broadcast a message to clients.
        
        Args:
            message: Dict to be sent as JSON
            exclude_client: Optional client_id to exclude from broadcast
            target_type: Optional client type to target (e.g., "ui", "agent")
        """
        message_json = json.dumps(message)
        
        # Determine target connections
        if target_type:
            target_clients = self.connections_by_type.get(target_type, set())
        else:
            target_clients = set(self.active_connections.keys())
        
        # Remove excluded client
        if exclude_client and exclude_client in target_clients:
            target_clients.discard(exclude_client)
        
        # Send to all targets
        disconnected = []
        for client_id in target_clients:
            try:
                ws = self.active_connections[client_id]
                await ws.send_text(message_json)
            except RuntimeError:
                # Connection closed unexpectedly
                disconnected.append(client_id)
        
        # Clean up closed connections
        for client_id in disconnected:
            self.disconnect(client_id)
    
    async def send_personal(self, client_id: str, message: Dict):
        """Send a message to a specific client."""
        if client_id not in self.active_connections:
            return
        
        try:
            ws = self.active_connections[client_id]
            message_json = json.dumps(message)
            await ws.send_text(message_json)
        except RuntimeError:
            self.disconnect(client_id)
    
    def get_connected_clients(self, client_type: str = None) -> List[str]:
        """Get list of connected client IDs, optionally filtered by type."""
        if client_type:
            return list(self.connections_by_type.get(client_type, set()))
        return list(self.active_connections.keys())
    
    def get_client_info(self, client_id: str) -> Dict:
        """Get metadata for a specific client."""
        return self.client_metadata.get(client_id, {})
    
    def get_connection_stats(self) -> Dict:
        """Get statistics about current connections."""
        stats = {
            "total_connections": len(self.active_connections),
            "by_type": {
                client_type: len(clients) 
                for client_type, clients in self.connections_by_type.items()
            }
        }
        return stats
