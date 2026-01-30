"""
Pydantic models for WebSocket message schemas.
Standardizes all messages exchanged over WebSocket.
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Message type enumeration."""
    # Connection lifecycle
    CONNECTION = "connection"
    DISCONNECTION = "disconnection"
    
    # Game state
    GAME_STATE = "game_state"
    GAME_START = "game_start"
    GAME_END = "game_end"
    PHASE_UPDATE = "phase_update"
    
    # Player actions
    PLAYER_ACTION = "player_action"
    VOTE = "vote"
    NIGHT_ACTION = "night_action"
    
    # Agent communication
    AGENT_MESSAGE = "agent_message"
    AGENT_DECISION = "agent_decision"
    
    # UI/System
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class BaseMessage(BaseModel):
    """Base model for all WebSocket messages."""
    message_type: MessageType
    client_id: str
    timestamp: float
    data: Dict[str, Any] = Field(default_factory=dict)


class ConnectionMessage(BaseMessage):
    """Message sent when client connects."""
    message_type: MessageType = MessageType.CONNECTION
    client_type: str = "ui"  # "ui", "agent", "observer"
    client_name: Optional[str] = None


class GameStateMessage(BaseMessage):
    """Broadcast current game state to all clients."""
    message_type: MessageType = MessageType.GAME_STATE
    phase: str  # "setup", "day", "night", "voting", "end"
    players: List[Dict[str, Any]] = []
    current_turn: int = 0
    alive_count: int = 0
    dead_count: int = 0


class AgentMessageContent(BaseMessage):
    """Agent speaking during day/discussion phase."""
    message_type: MessageType = MessageType.AGENT_MESSAGE
    agent_id: str
    agent_name: str
    message_text: str
    phase: str = "discussion"


class PlayerActionMessage(BaseMessage):
    """Player action (vote, night action, etc)."""
    message_type: MessageType = MessageType.PLAYER_ACTION
    action_type: str  # "vote", "target", "reveal", etc
    player_id: str
    target_id: Optional[str] = None
    target_name: Optional[str] = None


class PhaseUpdateMessage(BaseMessage):
    """Notification that game phase changed."""
    message_type: MessageType = MessageType.PHASE_UPDATE
    old_phase: str
    new_phase: str
    description: str = ""


class ErrorMessage(BaseMessage):
    """Error message sent to client."""
    message_type: MessageType = MessageType.ERROR
    error_code: str
    error_text: str
    context: Optional[Dict[str, Any]] = None


class PingMessage(BaseMessage):
    """Heartbeat ping to keep connection alive."""
    message_type: MessageType = MessageType.PING
    data: Dict[str, Any] = Field(default_factory=lambda: {"check": "alive"})


class PongMessage(BaseMessage):
    """Response to ping."""
    message_type: MessageType = MessageType.PONG
    data: Dict[str, Any] = Field(default_factory=lambda: {"check": "alive"})


# Type union for convenience
WebSocketMessageUnion = (
    ConnectionMessage
    | GameStateMessage
    | AgentMessageContent
    | PlayerActionMessage
    | PhaseUpdateMessage
    | ErrorMessage
    | PingMessage
    | PongMessage
)
