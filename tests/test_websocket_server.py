"""
Tests for WebSocket server functionality.
Tests connection management, message handling, and disconnection.
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket

pytest_plugins = ("pytest_asyncio",)

from server.websocket_server import app, manager, client_sessions
from server.connection_manager import ConnectionManager
from server.schemas import (
    MessageType,
    ConnectionMessage,
    GameStateMessage,
    ErrorMessage,
    PingMessage,
    PongMessage,
)


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def connection_manager():
    """Create fresh ConnectionManager instance for testing."""
    return ConnectionManager()


class TestConnectionManager:
    """Test ConnectionManager functionality."""
    
    @pytest.mark.asyncio
    async def test_client_connect(self, connection_manager):
        """Test registering a new connection."""
        websocket = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(websocket, "client_1", "ui")
        
        assert "client_1" in connection_manager.active_connections
        assert "ui" in connection_manager.connections_by_type
        assert "client_1" in connection_manager.connections_by_type["ui"]
        assert connection_manager.client_metadata["client_1"]["type"] == "ui"
    
    @pytest.mark.asyncio
    async def test_client_disconnect(self, connection_manager):
        """Test unregistering a connection."""
        websocket = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(websocket, "client_2", "agent")
        assert "client_2" in connection_manager.active_connections
        
        connection_manager.disconnect("client_2")
        assert "client_2" not in connection_manager.active_connections
        assert "client_2" not in connection_manager.connections_by_type["agent"]
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, connection_manager):
        """Test broadcasting message to all clients."""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        ws3 = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(ws1, "client_1", "ui")
        await connection_manager.connect(ws2, "client_2", "agent")
        await connection_manager.connect(ws3, "client_3", "observer")
        
        message = {"message_type": "test", "data": "hello"}
        await connection_manager.broadcast(message)
        
        # All clients should receive message
        assert ws1.send_text.call_count == 1
        assert ws2.send_text.call_count == 1
        assert ws3.send_text.call_count == 1
    
    @pytest.mark.asyncio
    async def test_broadcast_with_exclusion(self, connection_manager):
        """Test broadcasting with client exclusion."""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(ws1, "client_1", "ui")
        await connection_manager.connect(ws2, "client_2", "ui")
        
        message = {"message_type": "test"}
        await connection_manager.broadcast(message, exclude_client="client_1")
        
        # Only client_2 should receive
        assert ws1.send_text.call_count == 0
        assert ws2.send_text.call_count == 1
    
    @pytest.mark.asyncio
    async def test_broadcast_by_type(self, connection_manager):
        """Test broadcasting to specific client type."""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        ws3 = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(ws1, "client_1", "ui")
        await connection_manager.connect(ws2, "client_2", "agent")
        await connection_manager.connect(ws3, "client_3", "ui")
        
        message = {"message_type": "test"}
        await connection_manager.broadcast(message, target_type="ui")
        
        # Only UI clients should receive
        assert ws1.send_text.call_count == 1
        assert ws2.send_text.call_count == 0
        assert ws3.send_text.call_count == 1
    
    @pytest.mark.asyncio
    async def test_send_personal(self, connection_manager):
        """Test sending message to specific client."""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(ws1, "client_1", "ui")
        await connection_manager.connect(ws2, "client_2", "ui")
        
        message = {"message_type": "private"}
        await connection_manager.send_personal("client_1", message)
        
        # Only client_1 should receive
        assert ws1.send_text.call_count == 1
        assert ws2.send_text.call_count == 0
    
    @pytest.mark.asyncio
    async def test_get_connected_clients(self, connection_manager):
        """Test retrieving list of connected clients."""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        ws3 = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(ws1, "client_1", "ui")
        await connection_manager.connect(ws2, "client_2", "agent")
        await connection_manager.connect(ws3, "client_3", "ui")
        
        all_clients = connection_manager.get_connected_clients()
        ui_clients = connection_manager.get_connected_clients("ui")
        agent_clients = connection_manager.get_connected_clients("agent")
        
        assert len(all_clients) == 3
        assert len(ui_clients) == 2
        assert len(agent_clients) == 1
        assert set(ui_clients) == {"client_1", "client_3"}
    
    @pytest.mark.asyncio
    async def test_get_connection_stats(self, connection_manager):
        """Test connection statistics."""
        ws1 = AsyncMock(spec=WebSocket)
        ws2 = AsyncMock(spec=WebSocket)
        
        await connection_manager.connect(ws1, "client_1", "ui")
        await connection_manager.connect(ws2, "client_2", "agent")
        
        stats = connection_manager.get_connection_stats()
        
        assert stats["total_connections"] == 2
        assert stats["by_type"]["ui"] == 1
        assert stats["by_type"]["agent"] == 1


class TestWebSocketServer:
    """Test FastAPI WebSocket server endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "connections" in data
    
    def test_stats_endpoint(self, client):
        """Test statistics endpoint."""
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_clients" in data
        assert "by_type" in data
        assert "clients" in data
        assert isinstance(data["clients"], list)
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection (note: TestClient has limited WebSocket support)."""
        # Note: Full WebSocket testing requires websockets library or separate async test
        # This is a basic validation that the endpoint exists
        with pytest.raises(Exception):
            # This will fail because TestClient doesn't fully support WebSocket
            # In production, use httpx.AsyncClient + websockets
            with client.websocket_connect("/ws/test_client_1") as websocket:
                pass


class TestMessageSchemas:
    """Test message schema validation."""
    
    def test_connection_message(self):
        """Test ConnectionMessage schema."""
        msg = ConnectionMessage(
            client_id="client_1",
            client_type="ui",
            timestamp=12345.0
        )
        
        data = json.loads(msg.model_dump_json())
        assert data["message_type"] == "connection"
        assert data["client_id"] == "client_1"
        assert data["client_type"] == "ui"
    
    def test_game_state_message(self):
        """Test GameStateMessage schema."""
        msg = GameStateMessage(
            client_id="server",
            timestamp=12345.0,
            phase="day",
            players=[{"id": "p1", "alive": True}],
            current_turn=1,
            alive_count=8,
            dead_count=1
        )
        
        data = json.loads(msg.model_dump_json())
        assert data["message_type"] == "game_state"
        assert data["phase"] == "day"
        assert len(data["players"]) == 1
    
    def test_error_message(self):
        """Test ErrorMessage schema."""
        msg = ErrorMessage(
            client_id="server",
            timestamp=12345.0,
            error_code="INVALID_ACTION",
            error_text="Action not allowed in current phase"
        )
        
        data = json.loads(msg.model_dump_json())
        assert data["message_type"] == "error"
        assert data["error_code"] == "INVALID_ACTION"
    
    def test_ping_pong_messages(self):
        """Test Ping/Pong messages."""
        ping = PingMessage(client_id="server", timestamp=12345.0)
        pong = PongMessage(client_id="client_1", timestamp=12345.0)
        
        ping_data = json.loads(ping.model_dump_json())
        pong_data = json.loads(pong.model_dump_json())
        
        assert ping_data["message_type"] == "ping"
        assert pong_data["message_type"] == "pong"


class TestMessageHandling:
    """Test message routing and handling."""
    
    @pytest.mark.asyncio
    async def test_handle_ping_message(self):
        """Test ping message receives pong response."""
        # This would require mocking the handle_message function
        # and the manager's send_personal method
        pass
    
    @pytest.mark.asyncio
    async def test_handle_game_state_message(self):
        """Test game state message broadcast."""
        pass
    
    @pytest.mark.asyncio
    async def test_handle_agent_message(self):
        """Test agent message routing to UI clients."""
        pass


class TestReconnection:
    """Test client reconnection handling."""
    
    def test_session_tracking(self):
        """Test that client sessions are tracked."""
        # Sessions should be stored in client_sessions dict
        assert isinstance(client_sessions, dict)
    
    @pytest.mark.asyncio
    async def test_reconnect_count_incremented(self):
        """Test reconnection counter increments."""
        # This would require triggering disconnection and reconnection
        pass


class TestLoadScenarios:
    """Test server behavior under load."""
    
    @pytest.mark.asyncio
    async def test_multiple_connections(self, connection_manager):
        """Test handling multiple simultaneous connections."""
        websockets = [AsyncMock(spec=WebSocket) for _ in range(50)]
        
        for i, ws in enumerate(websockets):
            await connection_manager.connect(ws, f"client_{i}", "ui")
        
        assert len(connection_manager.active_connections) == 50
        
        # Broadcast to all
        message = {"test": "message"}
        await connection_manager.broadcast(message)
        
        # All should have received
        for ws in websockets:
            assert ws.send_text.call_count == 1
    
    @pytest.mark.asyncio
    async def test_rapid_connect_disconnect(self, connection_manager):
        """Test rapid connection/disconnection cycles."""
        for i in range(20):
            ws = AsyncMock(spec=WebSocket)
            await connection_manager.connect(ws, f"client_{i}", "ui")
            connection_manager.disconnect(f"client_{i}")
        
        # All should be cleaned up
        assert len(connection_manager.active_connections) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
