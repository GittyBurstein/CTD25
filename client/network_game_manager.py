"""
Network Game Mode - WebSocket Integration for Chess Game
Extends the existing game with multiplayer functionality.
"""

import sys
from pathlib import Path

# Add paths to components
base_path = Path(__file__).parent.parent
sys.path.append(str(base_path / "server" / "interfaces"))
sys.path.append(str(base_path / "client" / "interfaces"))
sys.path.append(str(base_path / "shared" / "interfaces"))

from Game import Game
from EventBus import EventBus
from EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_STARTED, GAME_ENDED, INVALID_MOVE
from websocket_client import ChessWebSocketClient
import threading
import time
import logging

logger = logging.getLogger(__name__)


class NetworkGameManager:
    """Manages network functionality for the chess game."""
    
    def __init__(self, game: Game, event_bus: EventBus):
        self.game = game
        self.event_bus = event_bus
        self.websocket_client = ChessWebSocketClient()
        self.is_network_game = False
        self.is_my_turn = False
        self.my_color = None
        
        # Setup WebSocket event handlers
        self._setup_websocket_handlers()
        
        # Subscribe to game events
        self.event_bus.subscribe(MOVE_DONE, self)
        
        logger.info("Network Game Manager initialized")
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers."""
        self.websocket_client.on_connected = self._on_connected
        self.websocket_client.on_disconnected = self._on_disconnected
        self.websocket_client.on_room_created = self._on_room_created
        self.websocket_client.on_room_joined = self._on_room_joined
        self.websocket_client.on_move_received = self._on_move_received
        self.websocket_client.on_player_joined = self._on_player_joined
        self.websocket_client.on_player_left = self._on_player_left
        self.websocket_client.on_error = self._on_error
    
    def start_network_game(self, mode: str = "create", room_id: str = None):
        """Start a network game."""
        logger.info(f"Starting network game mode: {mode}")
        
        # Connect to server
        self.websocket_client.start_connection()
        
        # Wait for connection to establish
        max_wait = 50  # 5 seconds max
        wait_count = 0
        while not self.websocket_client.is_connected() and wait_count < max_wait:
            time.sleep(0.1)
            wait_count += 1
        
        if not self.websocket_client.is_connected():
            logger.error("Failed to connect to server")
            return False
        
        if mode == "create":
            self.websocket_client.create_room()
        elif mode == "join" and room_id:
            self.websocket_client.join_room(room_id)
        else:
            logger.error("Invalid network game mode")
            return False
        
        self.is_network_game = True
        return True
    
    def stop_network_game(self):
        """Stop network game and disconnect."""
        logger.info("Stopping network game")
        self.is_network_game = False
        self.websocket_client.stop_connection()
    
    def handle_event(self, event_type: str, data: dict):
        """Handle game events for network synchronization."""
        if not self.is_network_game:
            return
        
        if event_type == MOVE_DONE:
            # Send move to other players
            command = data.get('command')
            if command and hasattr(command, 'params') and len(command.params) >= 2:
                from_pos = self._convert_position_to_notation(command.params[0])
                to_pos = self._convert_position_to_notation(command.params[1])
                piece = command.piece_id[:2] if command.piece_id else ''
                
                self.websocket_client.make_move(from_pos, to_pos, piece)
                logger.info(f"Sent move to server: {from_pos} to {to_pos} (piece: {piece})")
            else:
                logger.warning("Invalid move data received from game")
    
    def update(self, event_type: str = None, data: dict = None):
        """Handle both EventBus events and regular updates."""
        # If called with parameters, handle as EventBus event
        if event_type is not None:
            self.handle_event(event_type, data or {})
        
        # Always update network state
        if self.is_network_game:
            self.websocket_client.process_incoming_messages()
    
    def _convert_position_to_notation(self, pos: tuple) -> str:
        """Convert (row, col) position to chess notation (e.g., (0, 0) -> 'a8')."""
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return "a1"
        
        row, col = pos
        if not (0 <= row < 8 and 0 <= col < 8):
            return "a1"
        
        file = chr(ord('a') + col)
        rank = str(8 - row)
        return f"{file}{rank}"
    
    def _convert_notation_to_position(self, notation: str) -> tuple:
        """Convert chess notation to (row, col) position (e.g., 'a8' -> (0, 0))."""
        if not isinstance(notation, str) or len(notation) != 2:
            return (0, 0)
        
        file, rank = notation[0], notation[1]
        if not ('a' <= file <= 'h' and '1' <= rank <= '8'):
            return (0, 0)
        
        col = ord(file) - ord('a')
        row = 8 - int(rank)
        return (row, col)
    
    # WebSocket Event Handlers
    def _on_connected(self):
        """Called when connected to server."""
        logger.info("🌐 Connected to chess server!")
        print("🌐 Connected to chess server!")
    
    def _on_disconnected(self):
        """Called when disconnected from server."""
        logger.info("🔌 Disconnected from chess server")
        print("🔌 Disconnected from chess server")
        self.is_network_game = False
    
    def _on_room_created(self, room_id: str, player_color: str):
        """Called when room is created."""
        self.my_color = player_color
        self.is_my_turn = (player_color == "white")
        
        logger.info(f"🎮 Room created! Room ID: {room_id}, Playing as: {player_color}")
        print(f"🎮 Room created!")
        print(f"📋 Room ID: {room_id}")
        print(f"⚪ You are playing as: {player_color}")
        print("👥 Waiting for opponent to join...")
    
    def _on_room_joined(self, room_id: str, player_color: str):
        """Called when joined a room."""
        self.my_color = player_color
        
        if player_color == "spectator":
            logger.info(f"👁️ Joined room {room_id} as spectator")
            print(f"👁️ Joined room {room_id} as spectator")
        else:
            self.is_my_turn = (player_color == "white")
            logger.info(f"🎮 Joined room {room_id} as {player_color}")
            print(f"🎮 Joined room {room_id}!")
            print(f"⚪ You are playing as: {player_color}")
    
    def _on_move_received(self, move_data: dict):
        """Called when a move is received from opponent."""
        from_notation = move_data.get('from', 'a1')
        to_notation = move_data.get('to', 'a1')
        player = move_data.get('player', 'unknown')
        
        # Don't process our own moves
        if player == self.my_color:
            return
        
        from_pos = self._convert_notation_to_position(from_notation)
        to_pos = self._convert_notation_to_position(to_notation)
        
        logger.info(f"📥 Received opponent move: {from_notation} to {to_notation}")
        print(f"📥 Opponent moved: {from_notation} → {to_notation}")
        
        # Apply the move to our game
        # Note: This would need integration with your game's move system
        # For now, we'll just log it
        
        # Update turn
        self.is_my_turn = (player != self.my_color)
    
    def _on_player_joined(self, data: dict):
        """Called when a player joins the room."""
        players_count = data.get('players_count', 0)
        logger.info(f"👥 Player joined! Players in room: {players_count}")
        
        if players_count == 2:
            print("✅ Opponent joined! Game can begin!")
            print("🎯 Your turn!" if self.is_my_turn else "⏳ Wait for opponent's move")
        else:
            print(f"👥 Player joined (Total: {players_count}/2)")
    
    def _on_player_left(self, data: dict):
        """Called when a player leaves the room."""
        players_count = data.get('players_count', 0)
        logger.info(f"👋 Player left! Players in room: {players_count}")
        print(f"👋 Player left the game (Remaining: {players_count})")
        
        if players_count < 2:
            print("⏳ Waiting for opponent to join...")
    
    def _on_error(self, error_message: str):
        """Called when there's an error."""
        logger.error(f"❌ Network error: {error_message}")
        print(f"❌ Network error: {error_message}")
    
    def get_network_status(self) -> dict:
        """Get current network game status."""
        return {
            'is_network_game': self.is_network_game,
            'connected': self.websocket_client.is_connected(),
            'room_info': self.websocket_client.get_room_info(),
            'my_color': self.my_color,
            'is_my_turn': self.is_my_turn
        }
