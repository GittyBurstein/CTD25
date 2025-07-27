import inspect
import pathlib
import pygame
import queue, threading, time, math
import cv2
from typing import List, Dict, Tuple, Optional
from It1_interfaces.Board import Board
from It1_interfaces.Command import Command
from It1_interfaces.Piece import Piece
from It1_interfaces.img import Img


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board, event_bus=None):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = {p.piece_id: p for p in pieces}
        self.board = board
        self.start_time = time.time()
        self.user_input_queue = queue.Queue()
        self.event_bus = event_bus
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }

        # --- שינויים: אתחול pygame window להציג משחק (גודל תלוי בגודל הלוח) ---
        pygame.init()
        pygame.font.init()  # Initialize font module
        self.window_width = self.board.W_cells * self.board.cell_W_pix
        self.window_height = self.board.H_cells * self.board.cell_H_pix
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Kung Fu Chess")
        self.clock = pygame.time.Clock()
        self._should_quit = False

    # ─── helpers ─────────────────────────────────────────────────────────────
    def game_time_ms(self) -> int:
        """Return the current game time in milliseconds."""
        return int((time.time() - self.start_time) * 1000)

    def clone_board(self) -> Board:
        """
        Return a **brand-new** Board wrapping a copy of the background pixels
        so we can paint sprites without touching the pristine board.
        """
        return self.board.clone()

    def _draw(self):
        """Draw the current game state."""
        board_img = self.clone_board().img
        for piece in self.pieces.values():
            piece.draw_on_board(board_img, self.game_time_ms())
        # Draw selection rectangles
        for player in ['A', 'B']:
            pos = self.selection[player]['pos']
            color = self.selection[player]['color']
            x = pos[1] * self.board.cell_W_pix
            y = pos[0] * self.board.cell_H_pix
            # בציור ב־pygame נשנה:
            # במקום cv2.rectangle, נמיר את התמונה ל-surface ונצייר עליו רקטות

        # --- שינוי: המרה מ־board_img.img (OpenCV) ל־pygame Surface ---
        # נניח ש־board_img.img הוא numpy array בצבע BGR, נהפוך ל־RGB ואז ל־Surface:
        import numpy as np
        
        # Handle both BGR and BGRA images
        if board_img.img.shape[2] == 4:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGRA2RGB)
        else:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGR2RGB)
            
        # Create pygame surface with proper orientation
        pygame_surface = pygame.surfarray.make_surface(img_rgb.swapaxes(0, 1))

        # עכשיו נוסיף ציור של הריבועים (Selection Rectangles) באמצעות pygame:
        for player in ['A', 'B']:
            pos = self.selection[player]['pos']
            color = self.selection[player]['color']
            rect = pygame.Rect(pos[1] * self.board.cell_W_pix, pos[0] * self.board.cell_H_pix,
                               self.board.cell_W_pix, self.board.cell_H_pix)
            pygame.draw.rect(pygame_surface, color, rect, 3)
            selected_piece = self.selection[player]['selected']
            if selected_piece:
                p_pos = selected_piece.current_state.physics.current_cell
                rect2 = pygame.Rect(p_pos[1] * self.board.cell_W_pix, p_pos[0] * self.board.cell_H_pix,
                                    self.board.cell_W_pix, self.board.cell_H_pix)
                pygame.draw.rect(pygame_surface, color, rect2, 5)

        self.screen.blit(pygame_surface, (0, 0))
        
        # Display piece states for debugging
        font = pygame.font.Font(None, 24)
        y_offset = 10
        for player in ['A', 'B']:
            selected = self.selection[player]['selected']
            if selected:
                state_text = f"Player {player}: {selected.piece_id} - State: {selected.current_state.state}"
                text_surface = font.render(state_text, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, y_offset))
                y_offset += 30
        
        pygame.display.flip()

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        if self.event_bus:
            from It1_interfaces.EventTypes import GAME_STARTED
            self.event_bus.publish(GAME_STARTED, {"time": self.game_time_ms()})
        print("Game started. Press ESC to exit at any time.")

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset(start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win() and not self._should_quit:
            now = self.game_time_ms()

            # (1) Update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (2) Handle pygame events here (השינוי העיקרי: הוצאת קבלת האירועים מהת'רד)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._should_quit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._should_quit = True
                    # Player A controls
                    elif event.key == pygame.K_UP:
                        self._move_selection('A', 'up')
                    elif event.key == pygame.K_DOWN:
                        self._move_selection('A', 'down')
                    elif event.key == pygame.K_LEFT:
                        self._move_selection('A', 'left')
                    elif event.key == pygame.K_RIGHT:
                        self._move_selection('A', 'right')
                    elif event.key == pygame.K_RETURN:
                        self._select_piece('A')
                    # Player B controls
                    elif event.key == pygame.K_w:
                        self._move_selection('B', 'up')
                    elif event.key == pygame.K_s:
                        self._move_selection('B', 'down')
                    elif event.key == pygame.K_a:
                        self._move_selection('B', 'left')
                    elif event.key == pygame.K_d:
                        self._move_selection('B', 'right')
                    elif event.key == pygame.K_SPACE:
                        self._select_piece('B')

            # (3) Handle queued Commands from input thread (אם יש)
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)
                if self.event_bus:
                    from It1_interfaces.EventTypes import MOVE_DONE
                    self.event_bus.publish(MOVE_DONE, {"command": cmd})

            # (4) Draw current position
            self._draw()

            # (5) Detect captures
            self._resolve_collisions()

            # הגבלת פריימרייט
            self.clock.tick(30)

        if self.event_bus:
            from It1_interfaces.EventTypes import GAME_ENDED
            self.event_bus.publish(GAME_ENDED, {"time": self.game_time_ms()})
        self._announce_win()
        pygame.quit()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd: Command):
        """Process player input commands."""
        if cmd.piece_id in self.pieces:
            now = self.game_time_ms()
            piece = self.pieces[cmd.piece_id]
            print(f"[GAME] Processing command {cmd.type} for piece {cmd.piece_id} - current state: {piece.current_state.state}")
            piece.on_command(cmd, now)
            print(f"[GAME] After command, piece {cmd.piece_id} state: {piece.current_state.state}")
        else:
            print(f"[GAME] Warning: Piece {cmd.piece_id} not found in pieces!")

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures based on chess-like rules."""
        positions: Dict[tuple, List[Piece]] = {}
        to_remove = []

        # Group pieces by their positions
        for piece in self.pieces.values():
            pos = piece.current_state.physics.get_pos()
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(piece)

        # Resolve collisions
        for pos, pieces_in_cell in positions.items():
            if len(pieces_in_cell) > 1:
                print(f"[DEBUG] 🔥 COLLISION at {pos}: {[p.piece_id + '(' + p.color + ')' for p in pieces_in_cell]}")
                
                # Separate pieces by color
                white_pieces = [p for p in pieces_in_cell if p.color == "White"]
                black_pieces = [p for p in pieces_in_cell if p.color == "Black"]
                
                # CRITICAL: Same color pieces should NOT attack each other!
                # If pieces of the same color collide, prevent the movement instead of removing pieces
                if len(white_pieces) > 1:
                    print(f"[DEBUG] 🚫 FRIENDLY COLLISION: Multiple white pieces at {pos} - blocking movement!")
                    # Keep the piece that was already there (not moving)
                    stationary_pieces = [p for p in white_pieces if not p.current_state.physics.is_moving and p.current_state.state not in ["move", "jump"]]
                    moving_pieces = [p for p in white_pieces if p.current_state.physics.is_moving or p.current_state.state in ["move", "jump"]]
                    
                    if stationary_pieces and moving_pieces:
                        # Block the moving piece by keeping it at its current position (before the collision)
                        for moving_piece in moving_pieces:
                            print(f"[DEBUG] 🛡️ Blocking movement of {moving_piece.piece_id} - friendly fire prevention")
                            # Keep the piece at its current position and stop the movement
                            moving_piece.current_state.physics.target_cell = moving_piece.current_state.physics.current_cell
                            moving_piece.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(cmd_type="idle", timestamp_ms=now, piece_id=moving_piece.piece_id)
                            moving_piece.on_command(idle_cmd, now)
                    elif len(white_pieces) > 1:
                        # If we can't determine which is moving, block all but the first by keeping them at current positions
                        print(f"[DEBUG] ⚠️  Fallback: Blocking all white pieces except first at {pos}")
                        for p in white_pieces[1:]:
                            # Keep the piece at its current position and stop the movement
                            p.current_state.physics.target_cell = p.current_state.physics.current_cell
                            p.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(cmd_type="idle", timestamp_ms=now, piece_id=p.piece_id)
                            p.on_command(idle_cmd, now)
                
                if len(black_pieces) > 1:
                    print(f"[DEBUG] 🚫 FRIENDLY COLLISION: Multiple black pieces at {pos} - blocking movement!")
                    # Keep the piece that was already there (not moving)
                    stationary_pieces = [p for p in black_pieces if not p.current_state.physics.is_moving and p.current_state.state not in ["move", "jump"]]
                    moving_pieces = [p for p in black_pieces if p.current_state.physics.is_moving or p.current_state.state in ["move", "jump"]]
                    
                    if stationary_pieces and moving_pieces:
                        # Block the moving piece by keeping it at its current position (before the collision)
                        for moving_piece in moving_pieces:
                            print(f"[DEBUG] 🛡️ Blocking movement of {moving_piece.piece_id} - friendly fire prevention")
                            # Keep the piece at its current position and stop the movement
                            moving_piece.current_state.physics.target_cell = moving_piece.current_state.physics.current_cell
                            moving_piece.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(cmd_type="idle", timestamp_ms=now, piece_id=moving_piece.piece_id)
                            moving_piece.on_command(idle_cmd, now)
                    elif len(black_pieces) > 1:
                        # If we can't determine which is moving, block all but the first by keeping them at current positions
                        print(f"[DEBUG] ⚠️  Fallback: Blocking all black pieces except first at {pos}")
                        for p in black_pieces[1:]:
                            # Keep the piece at its current position and stop the movement
                            p.current_state.physics.target_cell = p.current_state.physics.current_cell
                            p.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(cmd_type="idle", timestamp_ms=now, piece_id=p.piece_id)
                            p.on_command(idle_cmd, now)
                
                # ONLY pieces of different colors can capture each other
                if white_pieces and black_pieces:
                    print(f"[DEBUG] ⚔️  ENEMY COLLISION: White vs Black at {pos}")
                    # Find who moved to this position (attacker wins)
                    attacking_piece = None
                    defending_piece = None
                    
                    # Determine attacker vs defender
                    for piece in pieces_in_cell:
                        # Check if this piece is currently moving or just completed a move
                        if (piece.current_state.physics.is_moving or 
                            piece.current_state.state in ["move", "jump"]):
                            attacking_piece = piece
                        else:
                            defending_piece = piece
                    
                    # If we can't determine attacker clearly, use the most recent mover
                    if not attacking_piece:
                        # Use the piece with the most recent action time as attacker
                        if hasattr(pieces_in_cell[0], 'last_action_time'):
                            attacking_piece = max(pieces_in_cell, key=lambda p: getattr(p, 'last_action_time', 0))
                            defending_piece = min(pieces_in_cell, key=lambda p: getattr(p, 'last_action_time', 0))
                        else:
                            # Fallback: first piece attacks
                            attacking_piece = pieces_in_cell[0]
                            defending_piece = pieces_in_cell[1] if len(pieces_in_cell) > 1 else None
                    
                    # Remove the defending piece (the one being captured)
                    if defending_piece and attacking_piece != defending_piece:
                        to_remove.append(defending_piece)
                        print(f"[DEBUG] ⚔️  {attacking_piece.piece_id}({attacking_piece.color}) CAPTURES {defending_piece.piece_id}({defending_piece.color})")
                    else:
                        print(f"[DEBUG] ⚠️  Could not determine attacker/defender clearly")

        # Remove captured pieces
        for p in to_remove:
            if self.event_bus:
                from It1_interfaces.EventTypes import PIECE_CAPTURED
                self.event_bus.publish(PIECE_CAPTURED, {"piece": p})
            del self.pieces[p.piece_id]
            print(f"[DEBUG] 🗑️  Piece {p.piece_id}({p.color}) removed from game")

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        kings = [p for p in self.pieces.values() if p.piece_type == "King"]
        return False  # Temporary override to allow the game to continue

    def _announce_win(self):
        """Announce the winner."""
        kings = [p for p in self.pieces.values() if p.piece_type == "King"]
        if len(kings) == 1:
            print(f"Game Over! {kings[0].color} wins!")
        else:
            print("Game Over! It's a draw.")
        print("Game Over! Press any key to close the window.")
        # במקום cv2.waitKey, פשוט נמתין עם pygame
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    waiting = False

    def _move_selection(self, player, direction):
        # Move the selection cursor for the given player
        pos = self.selection[player]['pos']
        print(f"[DEBUG] Current selection position for player {player}: {pos}")

        if direction == 'up' and pos[0] > 0:
            pos[0] -= 1
        elif direction == 'down' and pos[0] < self.board.H_cells - 1:
            pos[0] += 1
        elif direction == 'left' and pos[1] > 0:
            pos[1] -= 1
        elif direction == 'right' and pos[1] < self.board.W_cells - 1:
            pos[1] += 1

        print(f"[DEBUG] Updated selection position for player {player}: {pos}")
        pos_tuple = tuple(pos)
        if pos_tuple in self.pieces:
            print(f"[INFO] Player {player} selected piece state: {self.pieces[pos_tuple].current_state.state}")
        else:
            print(f"[INFO] No piece at position {pos_tuple} for player {player}.")

    def _select_piece(self, player):
        # Select or move a piece for the given player
        pos = tuple(self.selection[player]['pos'])
        selected = self.selection[player]['selected']
        player_color = "White" if player == "A" else "Black"
        print(f"[DEBUG] Player {player} (color: {player_color}) selection position: {pos}, selected: {selected}")

        if selected is None:
            # First keypress: select a piece at the cursor that belongs to this player
            for piece in self.pieces.values():
                p_pos = tuple(piece.current_state.physics.current_cell)
                if p_pos == pos and hasattr(piece, 'color') and piece.color == player_color:
                    self.selection[player]['selected'] = piece
                    print(f"[DEBUG] Player {player} selected piece: {piece.piece_id} (color: {piece.color})")
                    print(f"[DEBUG] Piece current state: {piece.current_state.state}")
                    break
            else:
                print(f"[DEBUG] No {player_color} piece found at position {pos} for player {player}")
        else:
            # Second keypress: try to move selected piece to cursor position
            start_pos = tuple(selected.current_state.physics.current_cell)
            moves = selected.current_state.moves
            valid_moves = moves.get_moves(start_pos[0], start_pos[1])
            print(f"[DEBUG] Valid moves for piece {selected.piece_id} from {start_pos}: {valid_moves}")
            allowed = False
            for move in valid_moves:
                if move == pos:
                    allowed = True
                    break
            if allowed:
                now = self.game_time_ms()
                print(f"[DEBUG] Creating move command for piece {selected.piece_id}: start_pos={start_pos}, target_pos={pos}")
                cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                print(f"[DEBUG] Move command created: {cmd}")
                self.user_input_queue.put(cmd)
                print(f"[DEBUG] Piece state before command: {selected.current_state.state}")
            else:
                print(f"[DEBUG] Move not allowed for piece {selected.piece_id} to position {pos}")
            self.selection[player]['selected'] = None
