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
from It1_interfaces.GameUI import GameUI


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board, event_bus=None, score_manager=None, move_logger=None):
        """Initialize the game with pieces, board, and optional event bus and managers."""
        self.pieces = {p.piece_id: p for p in pieces}
        self.board = board
        self.start_time = time.time()
        self.user_input_queue = queue.Queue()
        self.event_bus = event_bus
        self.score_manager = score_manager
        self.move_logger = move_logger
        self.selection = {
            'A': {'pos': [0, 0], 'selected': None, 'color': (255, 0, 0)},
            'B': {'pos': [7, 7], 'selected': None, 'color': (0, 0, 255)}
        }

        # --- שינויים: אתחול pygame window להציג משחק (גודל תלוי בגודל הלוח) ---
        pygame.init()
        pygame.font.init()  # Initialize font module
        self.board_width = self.board.W_cells * self.board.cell_W_pix
        self.board_height = self.board.H_cells * self.board.cell_H_pix
        self.info_panel_width = 250  # רוחב כל פאנל מידע (שניים)
        self.window_width = self.board_width + (2 * self.info_panel_width)  # פאנל משמאל ומימין
        self.window_height = self.board_height
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Kung Fu Chess")
        self.clock = pygame.time.Clock()
        self._should_quit = False
        
        # אתחול ממשק המשתמש
        self.ui = GameUI(self.info_panel_width)

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
        """Draw the current game state with info panel."""
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Draw game board
        board_img = self.clone_board().img
        for piece in self.pieces.values():
            piece.draw_on_board(board_img, self.game_time_ms())
        
        # Draw selection rectangles
        for player in ['A', 'B']:
            pos = self.selection[player]['pos']
            color = self.selection[player]['color']
            x = pos[1] * self.board.cell_W_pix
            y = pos[0] * self.board.cell_H_pix

        # --- שינוי: המרה מ־board_img.img (OpenCV) ל־pygame Surface ---
        import numpy as np
        
        # Handle both BGR and BGRA images
        if board_img.img.shape[2] == 4:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGRA2RGB)
        else:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGR2RGB)
            
        # Create pygame surface with proper orientation
        pygame_surface = pygame.surfarray.make_surface(img_rgb.swapaxes(0, 1))

        # ציור ריבועי הבחירה על הלוח
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

        # הצגת הלוח במיקום הנכון (אמצע המסך)
        board_x_offset = self.info_panel_width  # הזחה כדי לשים את הלוח באמצע
        self.screen.blit(pygame_surface, (board_x_offset, 0))
        
        # ציור שני פאנלי המידע באמצעות GameUI
        self.ui.draw_player_panels(self.screen, self.board_width, self.window_height, 
                                  self.pieces, self.selection, self.start_time, 
                                  self.score_manager, self.move_logger)
        
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
                    elif event.key == pygame.K_TAB:
                        # Display live statistics
                        self._display_live_statistics()
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
        
        # Display final statistics before announcing winner
        self._display_final_statistics()
        
        self._announce_win()
        pygame.quit()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd: Command):
        """Process player input commands."""
        if cmd.piece_id in self.pieces:
            now = self.game_time_ms()
            piece = self.pieces[cmd.piece_id]
            piece.on_command(cmd, now)
        else:
            pass  # Piece not found - silently ignore

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
                # Separate pieces by color
                white_pieces = [p for p in pieces_in_cell if p.color == "White"]
                black_pieces = [p for p in pieces_in_cell if p.color == "Black"]
                
                # CRITICAL: Same color pieces should NOT attack each other!
                # If pieces of the same color collide, prevent the movement instead of removing pieces
                if len(white_pieces) > 1:
                    # Keep the piece that was already there (not moving)
                    stationary_pieces = [p for p in white_pieces if not p.current_state.physics.is_moving and p.current_state.state not in ["move", "jump"]]
                    moving_pieces = [p for p in white_pieces if p.current_state.physics.is_moving or p.current_state.state in ["move", "jump"]]
                    
                    if stationary_pieces and moving_pieces:
                        # Block the moving piece by keeping it at its current position (before the collision)
                        for moving_piece in moving_pieces:
                            # Keep the piece at its current position and stop the movement
                            moving_piece.current_state.physics.target_cell = moving_piece.current_state.physics.current_cell
                            moving_piece.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(timestamp=now, piece_id=moving_piece.piece_id, type="idle", params=[])
                            moving_piece.on_command(idle_cmd, now)
                    elif len(white_pieces) > 1:
                        # If we can't determine which is moving, block all but the first by keeping them at current positions
                        for p in white_pieces[1:]:
                            # Keep the piece at its current position and stop the movement
                            p.current_state.physics.target_cell = p.current_state.physics.current_cell
                            p.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(timestamp=now, piece_id=p.piece_id, type="idle", params=[])
                            p.on_command(idle_cmd, now)
                
                if len(black_pieces) > 1:
                    # Keep the piece that was already there (not moving)
                    stationary_pieces = [p for p in black_pieces if not p.current_state.physics.is_moving and p.current_state.state not in ["move", "jump"]]
                    moving_pieces = [p for p in black_pieces if p.current_state.physics.is_moving or p.current_state.state in ["move", "jump"]]
                    
                    if stationary_pieces and moving_pieces:
                        # Block the moving piece by keeping it at its current position (before the collision)
                        for moving_piece in moving_pieces:
                            # Keep the piece at its current position and stop the movement
                            moving_piece.current_state.physics.target_cell = moving_piece.current_state.physics.current_cell
                            moving_piece.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(timestamp=now, piece_id=moving_piece.piece_id, type="idle", params=[])
                            moving_piece.on_command(idle_cmd, now)
                    elif len(black_pieces) > 1:
                        # If we can't determine which is moving, block all but the first by keeping them at current positions
                        for p in black_pieces[1:]:
                            # Keep the piece at its current position and stop the movement
                            p.current_state.physics.target_cell = p.current_state.physics.current_cell
                            p.current_state.physics.is_moving = False
                            # Force the piece back to idle state
                            now = self.game_time_ms()
                            idle_cmd = Command(timestamp=now, piece_id=p.piece_id, type="idle", params=[])
                            p.on_command(idle_cmd, now)
                
                # ONLY pieces of different colors can capture each other
                if white_pieces and black_pieces:
                    print(f"[DEBUG]  ENEMY COLLISION: White vs Black at {pos}")
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
                    # No print statement for captures

        # Remove captured pieces
        for p in to_remove:
            if self.event_bus:
                from It1_interfaces.EventTypes import PIECE_CAPTURED
                self.event_bus.publish(PIECE_CAPTURED, {"piece": p})
            del self.pieces[p.piece_id]

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        kings = [p for p in self.pieces.values() if p.piece_type == "K"]
        # Game ends when one or both kings are captured
        if len(kings) < 2:
            return True
        return False

    def _announce_win(self):
        """Announce the winner."""
        kings = [p for p in self.pieces.values() if p.piece_type == "K"]
        if len(kings) == 1:
            # One king survived - that color wins
            winner_color = kings[0].color
            print(f"🎉 Game Over! {winner_color} wins! 🎉")
            print(f"The {winner_color} king survived and conquered the battlefield!")
        elif len(kings) == 0:
            # Both kings are dead - it's a draw
            print("💀 Game Over! Both kings have fallen - It's a draw! 💀")
        else:
            # This shouldn't happen in normal gameplay
            print("Game Over! Unexpected end condition.")
        
        print("Press any key to close the window.")
        # במקום cv2.waitKey, פשוט נמתין עם pygame
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    waiting = False

    def _display_final_statistics(self):
        """Display final game statistics from all managers."""
        print("\n" + "="*60)
        print("🎮 FINAL GAME STATISTICS 🎮")
        print("="*60)
        
        # Try to get statistics from event managers (if they exist in main.py)
        # This is a safe way to access the managers without direct coupling
        game_duration = time.time() - self.start_time
        
        print(f"⏱️  Game Duration: {game_duration:.1f} seconds")
        print(f"🎯 Total Pieces Remaining: {len(self.pieces)}")
        
        # Count remaining pieces by color
        white_pieces = len([p for p in self.pieces.values() if hasattr(p, 'color') and p.color == "White"])
        black_pieces = len([p for p in self.pieces.values() if hasattr(p, 'color') and p.color == "Black"])
        
        print(f"⚪ White Pieces: {white_pieces}")
        print(f"⚫ Black Pieces: {black_pieces}")
        
        # Count pieces by type
        piece_counts = {}
        for piece in self.pieces.values():
            if hasattr(piece, 'piece_type'):
                piece_type = piece.piece_type
                if piece_type not in piece_counts:
                    piece_counts[piece_type] = {"White": 0, "Black": 0}
                if hasattr(piece, 'color'):
                    piece_counts[piece_type][piece.color] += 1
        
        print("\n📊 Remaining Pieces by Type:")
        piece_names = {"P": "Pawns", "R": "Rooks", "N": "Knights", "B": "Bishops", "Q": "Queens", "K": "Kings"}
        for piece_type, counts in piece_counts.items():
            name = piece_names.get(piece_type, f"Type {piece_type}")
            print(f"   {name}: White {counts['White']}, Black {counts['Black']}")
        
        print("="*60)

    def _display_live_statistics(self):
        """Display live game statistics during gameplay."""
        print("\n" + "="*50)
        print("📊 LIVE GAME STATISTICS 📊")
        print("="*50)
        
        game_duration = time.time() - self.start_time
        print(f"⏱️  Game Time: {game_duration:.1f}s")
        
        # Count current pieces
        white_pieces = len([p for p in self.pieces.values() if hasattr(p, 'color') and p.color == "White"])
        black_pieces = len([p for p in self.pieces.values() if hasattr(p, 'color') and p.color == "Black"])
        
        print(f"⚪ White Pieces: {white_pieces}")
        print(f"⚫ Black Pieces: {black_pieces}")
        
        # Count kings specifically
        kings = [p for p in self.pieces.values() if p.piece_type == "K"]
        white_kings = len([k for k in kings if k.color == "White"])
        black_kings = len([k for k in kings if k.color == "Black"])
        
        print(f"👑 Kings: White {white_kings}, Black {black_kings}")
        
        # Check pieces in different states
        moving_pieces = len([p for p in self.pieces.values() if p.current_state.physics.is_moving])
        idle_pieces = len([p for p in self.pieces.values() if p.current_state.state == "idle"])
        
        print(f"🏃 Moving Pieces: {moving_pieces}")
        print(f"💤 Idle Pieces: {idle_pieces}")
        
        print("="*50)
        print("Press TAB again for updated stats, ESC to quit")

    def _is_path_blocked(self, start_pos, end_pos, piece):
        """Check if the path from start_pos to end_pos is blocked by other pieces."""
        # Knights can jump over other pieces
        if piece.piece_type == "N":
            return False
        
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Calculate direction of movement
        row_dir = 0 if start_row == end_row else (1 if end_row > start_row else -1)
        col_dir = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        
        # Check each square along the path (excluding start and end)
        current_row = start_row + row_dir
        current_col = start_col + col_dir
        
        while (current_row, current_col) != (end_row, end_col):
            # Check if there's a piece at this position
            for p in self.pieces.values():
                piece_pos = tuple(p.current_state.physics.current_cell)
                if piece_pos == (current_row, current_col):
                    return True
            
            # Move to next position along the path
            current_row += row_dir
            current_col += col_dir
        
        return False

    def _move_selection(self, player, direction):
        # Move the selection cursor for the given player
        pos = self.selection[player]['pos']

        if direction == 'up' and pos[0] > 0:
            pos[0] -= 1
        elif direction == 'down' and pos[0] < self.board.H_cells - 1:
            pos[0] += 1
        elif direction == 'left' and pos[1] > 0:
            pos[1] -= 1
        elif direction == 'right' and pos[1] < self.board.W_cells - 1:
            pos[1] += 1

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
                # Check for path blocking and friendly fire BEFORE sending the move command
                if self._is_path_blocked(start_pos, pos, selected):
                    print(f"[DEBUG] 🚫 PATH BLOCKED: Cannot move {selected.piece_id} from {start_pos} to {pos} - path is blocked!")
                else:
                    target_piece = None
                    for piece in self.pieces.values():
                        if tuple(piece.current_state.physics.current_cell) == pos:
                            target_piece = piece
                            break
                    
                    move_blocked = False
                    
                    # Special pawn rules: can only capture diagonally, can only move straight to empty squares
                    if selected.piece_type == "P":
                        row_diff = abs(pos[0] - start_pos[0])
                        col_diff = abs(pos[1] - start_pos[1])
                        
                        # Check if this is a double move (2 squares) and if the pawn has already moved
                        if row_diff == 2 and hasattr(selected, 'has_moved') and selected.has_moved:
                            print(f"[DEBUG] 🚫 PAWN RULE: Pawn {selected.piece_id} cannot move 2 squares - already moved before!")
                            move_blocked = True
                        elif target_piece:  # There's a piece at target - trying to capture
                            if col_diff == 0:  # Moving straight - cannot capture
                                print(f"[DEBUG] 🚫 PAWN RULE: Pawn {selected.piece_id} cannot capture {target_piece.piece_id} by moving straight!")
                                move_blocked = True
                            elif col_diff == 1 and row_diff == 1:  # Diagonal capture - OK
                                print(f"[DEBUG] ✅ PAWN CAPTURE: Pawn {selected.piece_id} can capture {target_piece.piece_id} diagonally")
                            else:
                                print(f"[DEBUG] 🚫 PAWN RULE: Invalid diagonal for pawn capture")
                                move_blocked = True
                        else:  # Empty square - trying to move
                            if col_diff != 0:  # Moving diagonally to empty square - not allowed
                                print(f"[DEBUG] 🚫 PAWN RULE: Pawn {selected.piece_id} cannot move diagonally to empty square!")
                                move_blocked = True
                            else:
                                print(f"[DEBUG] ✅ PAWN MOVE: Pawn {selected.piece_id} moving straight to empty square")
                    
                    # If there's a piece at the target position with the same color, block the move
                    if target_piece and hasattr(target_piece, 'color') and hasattr(selected, 'color') and target_piece.color == selected.color:
                        print(f"[DEBUG] 🚫 FRIENDLY FIRE PREVENTION: Cannot move {selected.piece_id}({selected.color}) to attack {target_piece.piece_id}({target_piece.color}) - same color!")
                        move_blocked = True
                    
                    # Only proceed if move is not blocked
                    if not move_blocked:
                        now = self.game_time_ms()
                        print(f"[DEBUG] Creating move command for piece {selected.piece_id}: start_pos={start_pos}, target_pos={pos}")
                        cmd = Command.create_move_command(now, selected.piece_id, start_pos, pos)
                        print(f"[DEBUG] Move command created: {cmd}")
                        self.user_input_queue.put(cmd)
                        print(f"[DEBUG] Piece state before command: {selected.current_state.state}")
                    else:
                        print(f"[DEBUG] 🚫 Move blocked for {selected.piece_id} to {pos}")
            else:
                print(f"[DEBUG] Move not allowed for piece {selected.piece_id} to position {pos}")
            self.selection[player]['selected'] = None
