"""
Example WebSocket client to demonstrate server usage.
Connects to the WebSocket server and exchanges messages.

Usage:
    1. Start server: python -m server.websocket_server
    2. Run this client: python examples/websocket_client_example.py
"""

import asyncio
import json
import websockets
from datetime import datetime


async def run_example_client():
    """Connect to WebSocket server and demonstrate basic functionality."""
    
    uri = "ws://localhost:8000/ws/example_client_1?client_type=ui"
    
    print("🔌 Connecting to WebSocket server...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Connected to {uri}")
            
            # Receive welcome message
            welcome = await websocket.recv()
            print(f"📨 Received: {welcome}")
            
            # Send a ping
            ping_msg = {
                "message_type": "ping",
                "client_id": "example_client_1",
                "timestamp": datetime.now().timestamp()
            }
            await websocket.send(json.dumps(ping_msg))
            print(f"📤 Sent: ping")
            
            # Receive pong
            pong = await websocket.recv()
            print(f"📨 Received: {pong}")
            
            # Send a game state message (to be broadcast)
            game_state = {
                "message_type": "game_state",
                "client_id": "example_client_1",
                "timestamp": datetime.now().timestamp(),
                "phase": "day",
                "players": [
                    {"id": "player_1", "name": "Alice", "alive": True},
                    {"id": "player_2", "name": "Bob", "alive": True},
                ],
                "current_turn": 1,
                "alive_count": 2,
                "dead_count": 0
            }
            await websocket.send(json.dumps(game_state))
            print(f"📤 Sent: game_state (will be broadcast)")
            
            # Send agent message
            agent_msg = {
                "message_type": "agent_message",
                "client_id": "example_client_1",
                "timestamp": datetime.now().timestamp(),
                "agent_id": "agent_1",
                "agent_name": "Alice",
                "message_text": "Je pense que Bob est suspect!",
                "phase": "discussion"
            }
            await websocket.send(json.dumps(agent_msg))
            print(f"📤 Sent: agent_message")
            
            # Keep connection alive for a bit
            print("\n⏳ Keeping connection alive for 5 seconds...")
            await asyncio.sleep(5)
            
            print("👋 Closing connection...")
    
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed by server")
    except Exception as e:
        print(f"❌ Error: {e}")


async def multi_client_example():
    """Demonstrate multiple clients connecting simultaneously."""
    
    async def client_task(client_id: str, client_type: str):
        """Task for a single client."""
        uri = f"ws://localhost:8000/ws/{client_id}?client_type={client_type}"
        
        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ {client_id} ({client_type}) connected")
                
                # Receive welcome
                welcome = await websocket.recv()
                
                # Send a message
                msg = {
                    "message_type": "agent_message",
                    "client_id": client_id,
                    "timestamp": datetime.now().timestamp(),
                    "agent_id": client_id,
                    "agent_name": client_id,
                    "message_text": f"Hello from {client_id}!"
                }
                await websocket.send(json.dumps(msg))
                
                # Keep alive
                await asyncio.sleep(3)
                
                print(f"👋 {client_id} disconnecting")
        
        except Exception as e:
            print(f"❌ {client_id} error: {e}")
    
    print("🚀 Starting multiple clients...")
    
    # Create multiple client tasks
    tasks = [
        client_task("agent_1", "agent"),
        client_task("agent_2", "agent"),
        client_task("ui_client_1", "ui"),
        client_task("observer_1", "observer"),
    ]
    
    await asyncio.gather(*tasks)
    print("\n✅ All clients finished")


def main():
    """Run example."""
    print("=" * 60)
    print("WebSocket Client Example")
    print("=" * 60)
    print("\nMake sure the server is running:")
    print("  python -m server.websocket_server")
    print("\n" + "=" * 60 + "\n")
    
    # Run single client example
    print("1️⃣ Single Client Example:\n")
    asyncio.run(run_example_client())
    
    print("\n" + "=" * 60 + "\n")
    
    # Run multi-client example
    print("2️⃣ Multiple Clients Example:\n")
    asyncio.run(multi_client_example())
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
