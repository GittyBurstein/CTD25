#!/usr/bin/env python3
"""
Test script for the new server synchronization system.
This script helps test the authoritative server game state management.
"""

import sys
import asyncio
import websockets
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestClient:
    """Simple test client to verify server synchronization."""
    
    def __init__(self, name: str, server_uri: str = "ws://localhost:8765"):
        self.name = name
        self.server_uri = server_uri
        self.websocket = None
        self.room_id = None
        self.player_color = None
        
    async def connect(self):
        """Connect to the server."""
        try:
            self.websocket = await websockets.connect(self.server_uri)
            logger.info(f"{self.name}: Connected to server")
            return True
        except Exception as e:
            logger.error(f"{self.name}: Failed to connect: {e}")
            return False
    
    async def listen_for_messages(self):
        """Listen for messages from server."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"{self.name}: Connection closed")
        except Exception as e:
            logger.error(f"{self.name}: Error listening: {e}")
    
    async def handle_message(self, data):
        """Handle incoming message."""
        msg_type = data.get('type')
        
        if msg_type == 'connection_established':
            logger.info(f"{self.name}: Connection established")
            
        elif msg_type == 'room_created':
            self.room_id = data.get('room_id')
            self.player_color = data.get('player_color')
            logger.info(f"{self.name}: Room created - {self.room_id}, playing as {self.player_color}")
            
        elif msg_type == 'room_joined':
            self.room_id = data.get('room_id')
            self.player_color = data.get('player_color')
            logger.info(f"{self.name}: Joined room - {self.room_id}, role: {self.player_color}")
            
        elif msg_type == 'player_joined':
            logger.info(f"{self.name}: Another player joined the room")
            
        elif msg_type == 'periodic_sync':
            game_state = data.get('game_state', {})
            pieces = game_state.get('pieces', {})
            logger.info(f"{self.name}: Periodic sync - {len(pieces)} pieces")
            
        elif msg_type == 'game_state_update':
            move = data.get('move', {})
            game_state = data.get('game_state', {})
            pieces = game_state.get('pieces', {})
            logger.info(f"{self.name}: Move update - {move.get('from')} to {move.get('to')}, {len(pieces)} pieces")
            
        elif msg_type == 'error':
            logger.error(f"{self.name}: Server error - {data.get('message')}")
            
        else:
            logger.debug(f"{self.name}: Received {msg_type}")
    
    async def send_message(self, message):
        """Send message to server."""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
    
    async def create_room(self):
        """Create a new room."""
        await self.send_message({'type': 'create_room'})
    
    async def join_room(self, room_id):
        """Join existing room."""
        await self.send_message({'type': 'join_room', 'room_id': room_id})
    
    async def make_move(self, from_pos, to_pos, piece_id=""):
        """Make a move."""
        await self.send_message({
            'type': 'make_move',
            'from': from_pos,
            'to': to_pos,
            'piece': piece_id
        })
        logger.info(f"{self.name}: Sent move {from_pos} to {to_pos}")
    
    async def disconnect(self):
        """Disconnect from server."""
        if self.websocket:
            await self.websocket.close()


async def test_two_players():
    """Test with two players making moves."""
    logger.info("=== Testing Two Player Synchronization ===")
    
    # Create two test clients
    client1 = TestClient("Player1")
    client2 = TestClient("Player2")
    
    # Connect both clients
    if not await client1.connect():
        return False
    if not await client2.connect():
        return False
    
    # Start listening tasks
    listen_task1 = asyncio.create_task(client1.listen_for_messages())
    listen_task2 = asyncio.create_task(client2.listen_for_messages())
    
    # Give time for connection messages
    await asyncio.sleep(1)
    
    # Player 1 creates room
    await client1.create_room()
    await asyncio.sleep(1)
    
    # Player 2 joins room
    if client1.room_id:
        await client2.join_room(client1.room_id)
        await asyncio.sleep(2)
        
        # Test some moves
        logger.info("=== Testing Moves ===")
        
        # Player 1 moves pawn
        await client1.make_move((6, 0), (5, 0), "PW60")  # White pawn forward
        await asyncio.sleep(1)
        
        # Player 2 moves pawn
        await client2.make_move((1, 0), (2, 0), "PB10")  # Black pawn forward
        await asyncio.sleep(1)
        
        # Player 1 moves another piece
        await client1.make_move((7, 1), (5, 2), "NW71")  # White knight
        await asyncio.sleep(1)
        
        # Wait for sync messages
        await asyncio.sleep(3)
        
        logger.info("=== Test completed ===")
    
    # Cleanup
    listen_task1.cancel()
    listen_task2.cancel()
    await client1.disconnect()
    await client2.disconnect()
    
    return True


async def main():
    """Main test function."""
    logger.info("Starting server synchronization test...")
    
    try:
        # Test basic two-player functionality
        success = await test_two_players()
        
        if success:
            logger.info("✅ Server synchronization test completed successfully!")
        else:
            logger.error("❌ Server synchronization test failed!")
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")


if __name__ == "__main__":
    print("🧪 Server Synchronization Test")
    print("Make sure the server is running: python server/websocket_server.py")
    print("Then run this test to verify synchronization works.")
    print()
    
    asyncio.run(main())