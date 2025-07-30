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
        self.event_bus.subscribe(PIECE_CAPTURED, self)
        self.event_bus.subscribe("PIECE_SELECTED", self)
        self.event_bus.subscribe("PIECE_DESELECTED", self)
        
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
        self.websocket_client.on_game_state_received = self._on_game_state_received
        
        # Add handlers for new server messages
        self.websocket_client.on_authoritative_game_state = self._on_authoritative_game_state_received
        self.websocket_client.on_periodic_sync = self._on_periodic_sync_received
        self.websocket_client.on_game_state_update = self._on_game_state_update_received
        
        # Setup periodic game state sync (reduced frequency since server now manages state)
        self._sync_timer = 0
        self._sync_interval = 1000  # Reduced to every 1 second since server manages state
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
            # Send move to server for authoritative processing
            command = data.get('command')
            if command and hasattr(command, 'params') and len(command.params) >= 2:
                from_pos = command.params[0]  # Keep as coordinates
                to_pos = command.params[1]    # Keep as coordinates
                piece_id = command.piece_id if hasattr(command, 'piece_id') else ''
                
                # Send move to server for authoritative processing
                self.websocket_client.make_move(from_pos, to_pos, piece_id)
                logger.info(f"Sent move to server: {from_pos} to {to_pos} (piece: {piece_id})")
                
                # Don't process the move locally - wait for server response
                # The server will send back the authoritative game state
                
            else:
                logger.warning("Invalid move data received from game")
                
        # Since server now manages authoritative state, we don't need to send full state
        # The server will send us updates via periodic sync
        # Only send state occasionally for debugging/backup purposes
        current_time = self.game.game_time_ms()
        if not hasattr(self, '_last_sync_time'):
            self._last_sync_time = 0
        if (current_time - self._last_sync_time > 5000 and  # Only sync every 5 seconds for backup
            hasattr(self, 'room_id') and self.room_id):  # And only if in a room
            self._last_sync_time = current_time
            # Don't send full state anymore - server is authoritative
            # self._send_full_game_state()
    
    def _send_full_game_state(self):
        """Send complete game state to synchronize everything."""
        try:
            if not self.websocket_client.is_connected:
                return
                
            # Don't send state if we're not in a room or waiting for players
            if not hasattr(self, 'room_id') or not self.room_id:
                return
                
            # Get all piece positions and states
            pieces_state = {}
            for piece_id, piece in self.game.pieces.items():
                pieces_state[piece_id] = {
                    'position': piece.current_state.physics.current_board_cell,
                    'state': piece.current_state.current_state_name,
                    'is_moving': piece.current_state.physics.is_currently_moving,
                    'target_position': piece.current_state.physics.target_board_cell
                }
            
            # Get player selections
            selections = self.game.input_manager.get_all_selections()
            
            # Get game stats
            game_stats = {}
            if hasattr(self.game, 'score_manager'):
                game_stats['scores'] = self.game.score_manager.get_score()
            
            if hasattr(self.game, 'move_logger'):
                game_stats['moves_log'] = {
                    'A': self.game.move_logger.get_recent_moves_for_player('A'),
                    'B': self.game.move_logger.get_recent_moves_for_player('B')
                }
            
            game_state = {
                'type': 'game_state',
                'state': {
                    'pieces': pieces_state,
                    'selections': {
                        'A': {
                            'pos': selections['A']['pos'],
                            'selected_piece_id': selections['A']['selected'].piece_id if selections['A']['selected'] else None
                        },
                        'B': {
                            'pos': selections['B']['pos'], 
                            'selected_piece_id': selections['B']['selected'].piece_id if selections['B']['selected'] else None
                        }
                    },
                    'game_stats': game_stats,
                    'game_time': self.game.game_time_ms(),
                    'player': self.my_color
                }
            }
            
            self.websocket_client.send_message(game_state)
            
        except Exception as e:
            logger.error(f"Failed to send game state: {e}")
    
    def _on_game_state_received(self, state_data: dict):
        """Apply received game state to synchronize everything."""
        # This is now handled by the new authoritative handlers
        # Keep for backward compatibility but redirect to new handler
        self._apply_authoritative_game_state(state_data)
    
    def _on_authoritative_game_state_received(self, message_data: dict):
        """Handle authoritative game state from server."""
        game_state = message_data.get('game_state', {})
        self._apply_authoritative_game_state(game_state)
    
    def _on_periodic_sync_received(self, message_data: dict):
        """Handle periodic sync from server."""
        game_state = message_data.get('game_state', {})
        self._apply_authoritative_game_state(game_state)
    
    def _on_game_state_update_received(self, message_data: dict):
        """Handle game state update after a move."""
        game_state = message_data.get('game_state', {})
        move_data = message_data.get('move', {})
        
        logger.info(f"Received move update: {move_data}")
        self._apply_authoritative_game_state(game_state)
    
    def _apply_authoritative_game_state(self, state_data: dict):
        """Apply the authoritative game state from server."""
        try:
            # Check if data is wrapped in 'state' key (from server)
            if 'pieces' not in state_data and 'state' in state_data:
                state_data = state_data['state']
                
            pieces_state = state_data.get('pieces', {})
            
            # Apply piece positions and states from server
            for piece_id, piece_data in pieces_state.items():
                if piece_id in self.game.pieces:
                    piece = self.game.pieces[piece_id]
                    server_pos = piece_data.get('position', piece.current_state.physics.current_board_cell)
                    server_state = piece_data.get('state', 'idle')
                    is_moving = piece_data.get('is_moving', False)
                    target_pos = piece_data.get('target_position', server_pos)
                    
                    # Only update if position actually changed
                    current_pos = piece.current_state.physics.current_board_cell
                    if current_pos != server_pos:
                        piece.current_state.physics.current_board_cell = server_pos
                        piece.current_state.physics.target_board_cell = target_pos
                        
                        # Handle captured pieces (moved off board)
                        if server_pos == (-1, -1):
                            logger.info(f"Piece {piece_id} was captured")
                            # Hide captured piece
                            piece.current_state.physics.current_board_cell = (-1, -1)
                        
                        logger.debug(f"Updated piece {piece_id} position: {current_pos} -> {server_pos}")
            
            # Update game statistics if provided
            game_stats = state_data.get('game_stats', {})
            if game_stats and hasattr(self.game, 'score_manager'):
                scores = game_stats.get('scores', {})
                if scores:
                    # Update local score manager with server data
                    pass  # Score manager updates handled by server
                    
        except Exception as e:
            logger.error(f"Failed to apply authoritative game state: {e}")

    def _on_old_game_state_received(self, state_data: dict):
        """OLD: Apply received game state to synchronize everything."""
        try:
            # Check if data is wrapped in 'state' key (from server)
            if 'pieces' not in state_data and 'state' in state_data:
                state_data = state_data['state']
                
            player = state_data.get('player', 'unknown')
            
            # Don't apply our own state
            if player == self.my_color:
                return
                
            pieces_state = state_data.get('pieces', {})
            selections_state = state_data.get('selections', {})
            
            print(f"🔄 Syncing full game state from {player}")
            
            # Update all piece positions and states
            for piece_id, piece_data in pieces_state.items():
                if piece_id in self.game.pieces:
                    piece = self.game.pieces[piece_id]
                    
                    # Update position
                    new_pos = tuple(piece_data['position'])
                    old_pos = piece.current_state.physics.current_board_cell
                    
                    # Update the piece position
                    piece.current_state.physics.current_board_cell = new_pos
                    piece.current_state.physics.target_board_cell = tuple(piece_data['target_position'])
                    piece.current_state.physics.is_currently_moving = piece_data['is_moving']
                    
                    # Update board state if position changed
                    if old_pos != new_pos:
                        # Clear old position from board
                        if old_pos and old_pos in self.game.board.board_state:
                            self.game.board.board_state[old_pos] = None
                        
                        # Set new position on board
                        if new_pos:
                            self.game.board.board_state[new_pos] = piece
                    
                    # Update visual state
                    piece.current_state.state_start_time = self.game.game_time_ms()
                    
                    print(f"  🔧 Updated {piece_id}: {old_pos} -> {new_pos}")
            
            # Update selections (only show opponent's selection)
            opponent_player = 'A' if self.my_color == 'black' else 'B'
            if opponent_player in selections_state:
                opponent_selection = selections_state[opponent_player]
                
                # Update opponent's cursor position
                if hasattr(self.game.input_manager, '_player_positions'):
                    self.game.input_manager._player_positions[opponent_player] = tuple(opponent_selection['pos'])
                
                # Update opponent's selected piece
                selected_piece_id = opponent_selection.get('selected_piece_id')
                if selected_piece_id and selected_piece_id in self.game.pieces:
                    if hasattr(self.game.input_manager, '_player_selections'):
                        self.game.input_manager._player_selections[opponent_player] = self.game.pieces[selected_piece_id]
            
            # Update game stats
            game_stats = state_data.get('game_stats', {})
            if game_stats:
                # Update scores
                if 'scores' in game_stats and hasattr(self.game, 'score_manager'):
                    # Can't directly set scores, but we can log the sync
                    print(f"  📊 Received scores: {game_stats['scores']}")
                
                # Update moves log 
                if 'moves_log' in game_stats and hasattr(self.game, 'move_logger'):
                    # Can't directly set moves log, but we can log the sync
                    total_moves = len(game_stats['moves_log'].get('A', [])) + len(game_stats['moves_log'].get('B', []))
                    print(f"  📝 Received moves log with {total_moves} moves")
                
            print(f"✅ Game state synchronized")
            
        except Exception as e:
            logger.error(f"Failed to apply game state: {e}")
            import traceback
            traceback.print_exc()
    
    def update(self, event_type: str = None, data: dict = None):
        """Handle both EventBus events and regular updates."""
        # If called with parameters, handle as EventBus event
        if event_type is not None:
            self.handle_event(event_type, data or {})
        
        # Always update network state
        if self.is_network_game:
            self.websocket_client.process_incoming_messages()
            
            # Check if we need to sync state (only if there are other players)
            current_time = self.game.game_time_ms()
            if not hasattr(self, '_last_periodic_sync'):
                self._last_periodic_sync = 0
            # Only sync if enough time passed and we have room with other players
            if (current_time - self._last_periodic_sync > 500 and  # Less frequent sync
                hasattr(self, 'room_id') and self.room_id):
                self._last_periodic_sync = current_time
                self._send_full_game_state()
    
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
        if not notation or len(notation) != 2:
            return (0, 0)
        
        try:
            file = notation[0].lower()
            rank = notation[1]
            
            col = ord(file) - ord('a')
            row = 8 - int(rank)
            
            if not (0 <= row < 8 and 0 <= col < 8):
                return (0, 0)
            
            return (row, col)
        except (ValueError, IndexError):
            return (0, 0)
    
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
        self.room_id = None
        self.my_color = None
    
    def _on_room_created(self, room_id: str, player_color: str):
        """Called when room is created."""
        self.room_id = room_id
        self.my_color = player_color
        self.is_my_turn = (player_color == "white")
        
        # Update game's input manager with network settings
        if hasattr(self.game, 'input_manager'):
            self.game.input_manager.set_network_settings(
                is_network_game=True,
                my_player_color=player_color
            )
        
        logger.info(f"🎮 Room created! Room ID: {room_id}, Playing as: {player_color}")
        print(f"🎮 Room created!")
        print(f"📋 Room ID: {room_id}")
        print(f"⚪ You are playing as: {player_color}")
        print("👥 Waiting for opponent to join...")
    
    def _on_room_joined(self, room_id: str, player_color: str):
        """Called when joined a room."""
        self.room_id = room_id
        self.my_color = player_color
        
        # Update game's input manager with network settings
        if hasattr(self.game, 'input_manager'):
            self.game.input_manager.set_network_settings(
                is_network_game=True,
                my_player_color=player_color
            )
        
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
            print(f"🔄 Skipping own move: {from_notation} → {to_notation}")
            return
        
        from_pos = self._convert_notation_to_position(from_notation)
        to_pos = self._convert_notation_to_position(to_notation)
        
        logger.info(f"📥 Received opponent move: {from_notation} to {to_notation}")
        print(f"📥 Opponent moved: {from_notation} → {to_notation} (from {from_pos} to {to_pos})")
        
        # Apply the move to our game board
        try:
            # Debug: Check if we have access to pieces
            if hasattr(self.game, 'pieces'):
                pieces_dict = self.game.pieces
                print(f"🔍 Found {len(pieces_dict)} pieces in game.pieces")
            elif hasattr(self.game, 'board') and hasattr(self.game.board, 'pieces'):
                pieces_dict = {piece.piece_id: piece for piece in self.game.board.pieces}
                print(f"🔍 Found {len(pieces_dict)} pieces in game.board.pieces")
            else:
                print(f"❌ Could not find pieces in game object")
                return
            
            # Find the piece at the source position
            piece_to_move = None
            print(f"🔍 Looking for piece at position {from_pos}...")
            
            for piece_id, piece in pieces_dict.items():
                current_pos = piece.current_state.physics.current_board_cell
                print(f"   Piece {piece_id} at {current_pos}")
                if current_pos == from_pos:
                    piece_to_move = piece
                    print(f"✅ Found piece to move: {piece_id}")
                    break
            
            if piece_to_move:
                # Update the piece's physics position directly
                old_pos = piece_to_move.current_state.physics.current_board_cell
                piece_to_move.current_state.physics.current_board_cell = to_pos
                piece_to_move.current_state.physics.target_board_cell = to_pos
                piece_to_move.current_state.physics.is_currently_moving = False
                
                print(f"✅ Moved {piece_to_move.piece_id}: {old_pos} → {to_pos}")
                logger.info(f"✅ Applied opponent move: {piece_to_move.piece_id} to {to_pos}")
                
                # Force the piece to refresh its visual state
                piece_to_move.current_state.state_start_time = self.game.game_time_ms()
                
                print(f"🎨 Visual update forced for piece at {to_pos}")
                
            else:
                print(f"⚠️ No piece found at {from_pos}")
                logger.warning(f"⚠️ No piece found at {from_pos}")
            
            # Update turn
            self.is_my_turn = (player != self.my_color)
            print(f"🔄 Turn updated: is_my_turn = {self.is_my_turn}")
            
        except Exception as e:
            logger.error(f"❌ Failed to apply opponent move: {e}")
            print(f"❌ Error applying move: {e}")
            import traceback
            traceback.print_exc()
    
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
