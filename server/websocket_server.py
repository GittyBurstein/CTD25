"""
WebSocket Chess Server
Manages multiplayer chess games and client connections.
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from typing import Dict, Set, Optional, List
import uuid
import sys
from pathlib import Path

# Add paths to game components
base_path = Path(__file__).parent.parent
sys.path.append(str(base_path / "server" / "interfaces"))
sys.path.append(str(base_path / "shared" / "interfaces"))

# Import game components
try:
    from Game import Game
    from Board import Board
    from Piece import Piece
    from EventBus import EventBus
    from img import Img
    from PieceFactory import create_piece_states
    import csv
    import os
    import pathlib
    import numpy as np
except ImportError as e:
    logger.error(f"Failed to import game components: {e}")
    logger.info("Server will run in basic mode without game engine")
    Game = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ServerGameEngine:
    """Server-side game engine that manages the authoritative game state."""
    
    def __init__(self):
        self.game = None
        self.pieces = {}
        self.board = None
        self._initialize_game()
    
    def _initialize_game(self):
        """Initialize the server-side game engine."""
        try:
            # Check if game components are available
            if Game is None:
                logger.error("Game components not available - server running in basic mode")
                return
                
            # Initialize EventBus
            event_bus = EventBus()
            
            # Initialize the board image
            board_img = Img()
            try:
                board_img.read(pathlib.Path(base_path / "board.png"), size=(512, 512))
                logger.info("Server: Board image loaded successfully!")
            except Exception as e:
                logger.error(f"Server: Error loading board image: {e}")
                # Create a mock board image for server
                board_img.img = np.zeros((512, 512, 3), dtype=np.uint8)
            
            # Initialize the board
            self.board = Board(cell_H_pix=64, cell_W_pix=64, W_cells=8, H_cells=8, img=board_img)
            
            # Load initial positions from board.csv
            pieces = []
            board_csv_path = base_path / "pieces" / "board.csv"
            if not os.path.exists(board_csv_path):
                logger.error(f"Board CSV not found at {board_csv_path}")
                return
            
            # Piece creation functions should already be imported
            
            with open(board_csv_path, "r") as file:
                reader = csv.reader(file)
                for row_idx, row in enumerate(reader):
                    for col_idx, cell in enumerate(row):
                        if cell and len(cell) == 2:
                            piece_type, color_char = cell[0], cell[1]
                            color = "White" if color_char == "W" else "Black"
                            piece_id = f"{cell}{row_idx}{col_idx}"
                            
                            # Create piece with all its states
                            try:
                                idle_state = create_piece_states(cell, row_idx, col_idx, self.board)
                                piece = Piece(piece_id=piece_id, initial_state=idle_state, piece_type=piece_type)
                                piece.color = color
                                pieces.append(piece)
                                self.pieces[piece_id] = piece
                            except Exception as e:
                                logger.error(f"Failed to create piece {piece_id}: {e}")
            
            logger.info(f"Server: Loaded {len(pieces)} pieces")
            
            # Create the game instance (server-side, no UI)
            self.game = Game(pieces=pieces, board=self.board, event_bus=event_bus, 
                           score_manager=None, move_logger=None)
            
            logger.info("Server: Game engine initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize server game engine: {e}")
            raise
    
    def get_game_state(self):
        """Get the current authoritative game state."""
        if not self.game:
            return {}
        
        # Get all piece positions and states
        pieces_state = {}
        for piece_id, piece in self.pieces.items():
            try:
                pieces_state[piece_id] = {
                    'position': piece.current_state.physics.current_board_cell,
                    'state': piece.current_state.current_state_name,
                    'is_moving': piece.current_state.physics.is_currently_moving,
                    'target_position': piece.current_state.physics.target_board_cell,
                    'color': piece.color,
                    'piece_type': piece.piece_type
                }
            except Exception as e:
                logger.error(f"Error getting state for piece {piece_id}: {e}")
        
        return {
            'pieces': pieces_state,
            'game_time': self.game.game_time_ms() if hasattr(self.game, 'game_time_ms') else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def process_move(self, player_color: str, from_pos: tuple, to_pos: tuple, piece_id: str = None):
        """Process a move on the server side and return the result."""
        try:
            if not self.game:
                return False, "Game not initialized"
            
            # Find the piece at from_pos
            target_piece = None
            for pid, piece in self.pieces.items():
                if piece.current_state.physics.current_board_cell == from_pos:
                    # Check if this piece belongs to the player
                    if (player_color == "white" and piece.color == "White") or \
                       (player_color == "black" and piece.color == "Black"):
                        target_piece = piece
                        break
            
            if not target_piece:
                return False, f"No {player_color} piece found at {from_pos}"
            
            # Validate the move (basic validation)
            if not self._is_valid_move(target_piece, from_pos, to_pos):
                return False, "Invalid move"
            
            # Execute the move
            target_piece.current_state.physics.current_board_cell = to_pos
            target_piece.current_state.physics.target_board_cell = to_pos
            
            # Check for captures
            captured_piece = None
            for pid, piece in self.pieces.items():
                if piece != target_piece and piece.current_state.physics.current_board_cell == to_pos:
                    captured_piece = piece
                    break
            
            if captured_piece:
                # Remove captured piece
                captured_piece.current_state.physics.current_board_cell = (-1, -1)  # Off board
                logger.info(f"Piece captured: {captured_piece.piece_id}")
            
            logger.info(f"Move processed: {target_piece.piece_id} from {from_pos} to {to_pos}")
            return True, "Move successful"
            
        except Exception as e:
            logger.error(f"Error processing move: {e}")
            return False, f"Server error: {e}"
    
    def _is_valid_move(self, piece, from_pos: tuple, to_pos: tuple):
        """Basic move validation (can be enhanced with chess rules)."""
        # Basic bounds check
        if not (0 <= to_pos[0] < 8 and 0 <= to_pos[1] < 8):
            return False
        
        # Can't move to same position
        if from_pos == to_pos:
            return False
        
        # Add more chess-specific validation here if needed
        return True
    
    def update(self, dt: float):
        """Update the game state (called periodically)."""
        if self.game:
            try:
                # Update game logic
                pass  # Game update logic here if needed
            except Exception as e:
                logger.error(f"Error updating game: {e}")


class ChessGameRoom:
    """Represents a chess game room with two players."""
    
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: List[websockets.WebSocketServerProtocol] = []
        self.spectators: Set[websockets.WebSocketServerProtocol] = set()
        self.created_at = datetime.now()
        
        # Initialize server-side game engine
        self.game_engine = ServerGameEngine()
        
        # Game state is now managed by the server engine
        self.game_state = {
            'current_player': 'white',
            'moves_history': [],
            'game_status': 'waiting',  # waiting, active, finished
            'winner': None
        }
    
    def get_authoritative_game_state(self):
        """Get the authoritative game state from server engine."""
        engine_state = self.game_engine.get_game_state()
        return {
            **self.game_state,
            **engine_state
        }
    
    def add_player(self, websocket: websockets.WebSocketServerProtocol) -> bool:
        """Add a player to the room. Returns True if successful, False if room is full."""
        if len(self.players) < 2:
            self.players.append(websocket)
            if len(self.players) == 2:
                self.game_state['game_status'] = 'active'
            return True
        return False
    
    def remove_player(self, websocket: websockets.WebSocketServerProtocol):
        """Remove a player from the room."""
        if websocket in self.players:
            self.players.remove(websocket)
            if len(self.players) < 2:
                self.game_state['game_status'] = 'waiting'
    
    def add_spectator(self, websocket: websockets.WebSocketServerProtocol):
        """Add a spectator to the room."""
        self.spectators.add(websocket)
    
    def remove_spectator(self, websocket: websockets.WebSocketServerProtocol):
        """Remove a spectator from the room."""
        self.spectators.discard(websocket)
    
    def get_player_color(self, websocket: websockets.WebSocketServerProtocol) -> Optional[str]:
        """Get the color assigned to a player."""
        if websocket in self.players:
            return 'white' if self.players.index(websocket) == 0 else 'black'
        return None
    
    async def broadcast_to_room(self, message: dict, exclude: Optional[websockets.WebSocketServerProtocol] = None):
        """Broadcast a message to all players and spectators in the room."""
        all_clients = set(self.players) | self.spectators
        if exclude:
            all_clients.discard(exclude)
        
        message_str = json.dumps(message)
        disconnected = []
        
        for client in all_clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
        
        # Clean up disconnected clients
        for client in disconnected:
            self.remove_player(client)
            self.remove_spectator(client)


class ChessWebSocketServer:
    """Main WebSocket server for chess games."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.rooms: Dict[str, ChessGameRoom] = {}
        self.client_rooms: Dict[websockets.WebSocketServerProtocol, str] = {}
        self._running = False
        logger.info(f"Chess WebSocket Server initialized on {host}:{port}")
    
    async def _periodic_sync(self):
        """Periodically sync game state to all clients."""
        while self._running:
            try:
                for room_id, room in list(self.rooms.items()):
                    if len(room.players) >= 2 and room.game_state['game_status'] == 'active':
                        # Get authoritative state
                        auth_state = room.get_authoritative_game_state()
                        
                        # Broadcast to all clients in room
                        await room.broadcast_to_room({
                            'type': 'periodic_sync',
                            'game_state': auth_state,
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Sync every 100ms for smooth real-time experience
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in periodic sync: {e}")
                await asyncio.sleep(1)  # Wait longer on error
    
    async def register_client(self, websocket, path=None):
        """Handle client registration and message routing."""
        try:
            logger.info(f"Client connected from {websocket.remote_address}")
            await self.send_message(websocket, {
                'type': 'connection_established',
                'message': 'Connected to Chess Server',
                'server_time': datetime.now().isoformat()
            })
            
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {websocket.remote_address} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {websocket.remote_address}: {e}")
        finally:
            await self.cleanup_client(websocket)
    
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming message from client."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            # Only log important messages, not game_state spam
            if message_type != 'game_state':
                logger.info(f"Received message: {message_type} from {websocket.remote_address}")
            
            if message_type == 'create_room':
                await self.handle_create_room(websocket, data)
            elif message_type == 'join_room':
                await self.handle_join_room(websocket, data)
            elif message_type == 'list_rooms':
                await self.handle_list_rooms(websocket)
            elif message_type == 'make_move':
                await self.handle_make_move(websocket, data)
            elif message_type == 'game_state':
                await self.handle_game_state(websocket, data)
            elif message_type == 'chat_message':
                await self.handle_chat_message(websocket, data)
            elif message_type == 'ping':
                await self.send_message(websocket, {'type': 'pong', 'timestamp': datetime.now().isoformat()})
            else:
                await self.send_message(websocket, {
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
                
        except json.JSONDecodeError:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Invalid JSON format'
            })
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Internal server error'
            })
    
    async def handle_create_room(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle room creation request."""
        room_id = str(uuid.uuid4())[:8]  # Short unique ID
        room = ChessGameRoom(room_id)
        
        # Add creator as first player
        room.add_player(websocket)
        self.rooms[room_id] = room
        self.client_rooms[websocket] = room_id
        
        await self.send_message(websocket, {
            'type': 'room_created',
            'room_id': room_id,
            'player_color': 'white',
            'game_state': room.get_authoritative_game_state()
        })
        
        logger.info(f"Room {room_id} created by {websocket.remote_address}")
        logger.info(f"🎮 Room {room_id}: 1/2 players connected (waiting for opponent)")
    
    async def handle_join_room(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle room join request."""
        room_id = data.get('room_id')
        
        if room_id not in self.rooms:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Room not found'
            })
            return
        
        room = self.rooms[room_id]
        
        # Try to add as player first
        if room.add_player(websocket):
            self.client_rooms[websocket] = room_id
            player_color = room.get_player_color(websocket)
            
            await self.send_message(websocket, {
                'type': 'room_joined',
                'room_id': room_id,
                'player_color': player_color,
                'game_state': room.get_authoritative_game_state()
            })
            
            # Notify other players
            await room.broadcast_to_room({
                'type': 'player_joined',
                'room_id': room_id,
                'players_count': len(room.players),
                'game_state': room.get_authoritative_game_state()
            }, exclude=websocket)
            
            logger.info(f"Player joined room {room_id} as {player_color}")
            logger.info(f"🎮 Room {room_id}: {len(room.players)}/2 players connected")
            
            if len(room.players) == 2:
                logger.info(f"🎯 Room {room_id}: GAME READY! Both players connected")
            
        else:
            # Add as spectator
            room.add_spectator(websocket)
            self.client_rooms[websocket] = room_id
            
            await self.send_message(websocket, {
                'type': 'room_joined',
                'room_id': room_id,
                'player_color': 'spectator',
                'game_state': room.get_authoritative_game_state()
            })
            
            logger.info(f"Spectator joined room {room_id}")
    
    async def handle_list_rooms(self, websocket: websockets.WebSocketServerProtocol):
        """Handle request for available rooms."""
        rooms_info = []
        for room_id, room in self.rooms.items():
            rooms_info.append({
                'room_id': room_id,
                'players_count': len(room.players),
                'spectators_count': len(room.spectators),
                'game_status': room.game_state['game_status'],
                'created_at': room.created_at.isoformat()
            })
        
        await self.send_message(websocket, {
            'type': 'rooms_list',
            'rooms': rooms_info
        })
    
    async def handle_make_move(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle chess move from client."""
        room_id = self.client_rooms.get(websocket)
        if not room_id or room_id not in self.rooms:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Not in a room'
            })
            return
        
        room = self.rooms[room_id]
        player_color = room.get_player_color(websocket)
        
        if not player_color:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Only players can make moves'
            })
            return
        
        # Check if game has enough players
        if len(room.players) < 2:
            await self.send_message(websocket, {
                'type': 'error', 
                'message': 'Waiting for opponent to join'
            })
            return
        
        # Extract move data
        from_notation = data.get('from')
        to_notation = data.get('to')
        piece_id = data.get('piece', '')
        
        # Convert chess notation to board coordinates if needed
        from_pos = self._notation_to_coords(from_notation) if isinstance(from_notation, str) else from_notation
        to_pos = self._notation_to_coords(to_notation) if isinstance(to_notation, str) else to_notation
        
        # Process the move through the server game engine
        success, message = room.game_engine.process_move(player_color, from_pos, to_pos, piece_id)
        
        if not success:
            await self.send_message(websocket, {
                'type': 'error',
                'message': f'Invalid move: {message}'
            })
            return
        
        # Create move data for history
        move_data = {
            'from': from_pos,
            'to': to_pos,
            'piece': piece_id,
            'timestamp': datetime.now().isoformat(),
            'player': player_color,
            'success': True
        }
        
        # Add move to history
        room.game_state['moves_history'].append(move_data)
        
        # In Kung Fu Chess, we don't switch turns - both players can move simultaneously
        # room.game_state['current_player'] = 'black' if player_color == 'white' else 'white'
        
        # Get the updated authoritative game state
        updated_state = room.get_authoritative_game_state()
        
        # Broadcast the authoritative game state to all clients in room
        await room.broadcast_to_room({
            'type': 'game_state_update',
            'move': move_data,
            'game_state': updated_state,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Move processed in room {room_id}: {from_pos} to {to_pos} by {player_color}")
    
    async def handle_game_state(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle game state broadcast from client."""
        room_id = self.client_rooms.get(websocket)
        if not room_id or room_id not in self.rooms:
            return  # Don't even respond with error to reduce noise
        
        room = self.rooms[room_id]
        
        # Only process if there are other players in the room
        if len(room.players) < 2:
            return  # No processing needed
        
        # The server now manages the authoritative state
        # We don't accept client state updates - the server is the authority
        # Instead, we send the current authoritative state back
        
        authoritative_state = room.get_authoritative_game_state()
        
        # Send the authoritative state back to the requesting client
        await self.send_message(websocket, {
            'type': 'authoritative_game_state',
            'game_state': authoritative_state,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.debug(f"Sent authoritative game state to client in room {room_id}")
    
    def _notation_to_coords(self, notation):
        """Convert chess notation (like 'a1') to board coordinates (row, col)."""
        if isinstance(notation, tuple) and len(notation) == 2:
            return notation  # Already coordinates
        
        if isinstance(notation, str) and len(notation) == 2:
            col = ord(notation[0].lower()) - ord('a')  # a=0, b=1, etc.
            row = 8 - int(notation[1])  # 8=0, 7=1, etc. (flip for board coordinates)
            return (row, col)
        
        # If it's not proper notation, assume it's already coordinates
        return notation
    
    def _coords_to_notation(self, coords):
        """Convert board coordinates (row, col) to chess notation."""
        if isinstance(coords, str):
            return coords  # Already notation
        
        row, col = coords
        file = chr(ord('a') + col)  # 0=a, 1=b, etc.
        rank = str(8 - row)  # 0=8, 1=7, etc. (flip back from board coordinates)
        return f"{file}{rank}"
    
    async def handle_chat_message(self, websocket: websockets.WebSocketServerProtocol, data: dict):
        """Handle chat message from client."""
        room_id = self.client_rooms.get(websocket)
        if not room_id or room_id not in self.rooms:
            return
        
        room = self.rooms[room_id]
        player_color = room.get_player_color(websocket) or 'spectator'
        
        chat_message = {
            'type': 'chat_message',
            'player': player_color,
            'message': data.get('message', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        await room.broadcast_to_room(chat_message)
    
    async def cleanup_client(self, websocket: websockets.WebSocketServerProtocol):
        """Clean up when client disconnects."""
        room_id = self.client_rooms.get(websocket)
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
            room.remove_player(websocket)
            room.remove_spectator(websocket)
            
            # Remove empty rooms
            if len(room.players) == 0 and len(room.spectators) == 0:
                del self.rooms[room_id]
                logger.info(f"Removed empty room {room_id}")
            else:
                # Notify remaining clients
                await room.broadcast_to_room({
                    'type': 'player_left',
                    'room_id': room_id,
                    'players_count': len(room.players),
                    'game_state': room.get_authoritative_game_state()
                })
        
        if websocket in self.client_rooms:
            del self.client_rooms[websocket]
    
    async def send_message(self, websocket: websockets.WebSocketServerProtocol, message: dict):
        """Send a message to a specific client."""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            pass
    
    async def start_server(self):
        """Start the WebSocket server."""
        logger.info(f"Starting Chess WebSocket Server on {self.host}:{self.port}")
        
        self._running = True
        
        # Start periodic sync task
        sync_task = asyncio.create_task(self._periodic_sync())
        
        try:
            async with websockets.serve(self.register_client, self.host, self.port):
                logger.info("Chess WebSocket Server is running...")
                logger.info(f"Connect clients to: ws://{self.host}:{self.port}")
                logger.info("Periodic game state synchronization enabled (100ms intervals)")
                await asyncio.Future()  # Run forever
        finally:
            self._running = False
            sync_task.cancel()
            try:
                await sync_task
            except asyncio.CancelledError:
                pass


async def main():
    """Main entry point for the WebSocket server."""
    server = ChessWebSocketServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Chess WebSocket Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
