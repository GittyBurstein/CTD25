import pygame
import queue, threading, time, math
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
from It1_interfaces.Board import Board
from It1_interfaces.Command import Command
from It1_interfaces.Piece import Piece
from It1_interfaces.img import Img
from It1_interfaces.GameUI import GameUI
from It1_interfaces.StatisticsManager import StatisticsManager
from It1_interfaces.ThreadedInputManager import ThreadedInputManager
from It1_interfaces.EventTypes import GAME_STARTED, GAME_ENDED, MOVE_DONE, PIECE_CAPTURED


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
        
        # Initialize managers
        self.statistics_manager = StatisticsManager()
        self.input_manager = ThreadedInputManager(board, self.user_input_queue, debug=False)  # Set debug=True for verbose output

        # Cache board cell dimensions for performance
        self.cell_width = self.board.cell_W_pix
        self.cell_height = self.board.cell_H_pix

        # --- שינויים: אתחול pygame window להציג משחק (גודל תלוי בגודל הלוח) ---
        pygame.init()
        pygame.font.init()  # Initialize font module
        self.board_width = self.board.W_cells * self.cell_width
        self.board_height = self.board.H_cells * self.cell_height
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
        
        # Get player selections once
        selection = self.input_manager.get_all_selections()

        # --- שינוי: המרה מ־board_img.img (OpenCV) ל־pygame Surface ---
        
        # Handle both BGR and BGRA images
        if board_img.img.shape[2] == 4:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGRA2RGB)
        else:
            img_rgb = cv2.cvtColor(board_img.img, cv2.COLOR_BGR2RGB)
            
        # Create pygame surface with proper orientation
        pygame_surface = pygame.surfarray.make_surface(img_rgb.swapaxes(0, 1))

        # ציור ריבועי הבחירה על הלוח
        for player in ['A', 'B']:
            pos = selection[player]['pos']
            color = selection[player]['color']
            rect = pygame.Rect(pos[1] * self.cell_width, pos[0] * self.cell_height,
                               self.cell_width, self.cell_height)
            pygame.draw.rect(pygame_surface, color, rect, 3)
            selected_piece = selection[player]['selected']
            if selected_piece:
                p_pos = selected_piece.current_state.physics.current_cell
                rect2 = pygame.Rect(p_pos[1] * self.cell_width, p_pos[0] * self.cell_height,
                                    self.cell_width, self.cell_height)
                pygame.draw.rect(pygame_surface, color, rect2, 5)

        # הצגת הלוח במיקום הנכון (אמצע המסך)
        board_x_offset = self.info_panel_width  # הזחה כדי לשים את הלוח באמצע
        self.screen.blit(pygame_surface, (board_x_offset, 0))
        
        # ציור שני פאנלי המידע באמצעות GameUI
        self.ui.draw_player_panels(self.screen, self.board_width, self.window_height, 
                                  self.pieces, selection, self.start_time, 
                                  self.score_manager, self.move_logger)
        
        pygame.display.flip()

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        if self.event_bus:
            self.event_bus.publish(GAME_STARTED, {"time": self.game_time_ms()})
        print("Game started. Press ESC to exit at any time.")

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset(start_ms)

        # ═══════════ START THREADED INPUT MANAGER ═══════════
        self.input_manager.set_game_references(self.pieces, self.game_time_ms)
        self.input_manager.start_listening()
        print("🎮 Started threaded input manager")

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win() and not self._should_quit:
            now = self.game_time_ms()

            # (1) Update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (1.5) Handle pygame QUIT events (window close button)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._should_quit = True

            # (2) Handle queued Commands from input thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                
                # Handle system commands
                if cmd.piece_id == "SYSTEM":
                    if cmd.type == "QUIT":
                        self._should_quit = True
                        continue
                    elif cmd.type == "SHOW_STATS":
                        self.statistics_manager.display_live_statistics(self.pieces, self.start_time)
                        continue
                
                # Handle game commands
                self._process_input(cmd)
                if self.event_bus:
                    self.event_bus.publish(MOVE_DONE, {"command": cmd})

            # (3) Draw current position
            self._draw()

            # (4) Detect captures
            self._resolve_collisions()

            # הגבלת פריימרייט
            self.clock.tick(30)

        # ═══════════ STOP THREADED INPUT MANAGER ═══════════
        self.input_manager.stop_listening()
        print("🎮 Stopped threaded input manager")

        if self.event_bus:
            self.event_bus.publish(GAME_ENDED, {"time": self.game_time_ms()})
        
        # Display final statistics before announcing winner
        self.statistics_manager.display_final_statistics(self.pieces, self.start_time)
        
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
        now = self.game_time_ms()

        # Group pieces by their positions
        for piece in self.pieces.values():
            pos = piece.current_state.physics.get_pos(now)
            if pos not in positions:
                positions[pos] = []
            positions[pos].append(piece)

        # Resolve collisions
        for pos, pieces_in_cell in positions.items():
            if len(pieces_in_cell) > 1:
                # Separate pieces by color
                white_pieces = [p for p in pieces_in_cell if p.color == "White"]
                black_pieces = [p for p in pieces_in_cell if p.color == "Black"]
                
                # Handle same-color collisions (friendly fire prevention)
                for color_group in [white_pieces, black_pieces]:
                    if len(color_group) > 1:
                        self._handle_friendly_collision(color_group)
                
                # Handle different-color collisions (capture)
                if white_pieces and black_pieces:
                    self._handle_enemy_collision(pieces_in_cell, to_remove)

        # Remove captured pieces
        for p in to_remove:
            if self.event_bus:
                self.event_bus.publish(PIECE_CAPTURED, {"piece": p})
            del self.pieces[p.piece_id]

    def _handle_friendly_collision(self, same_color_pieces):
        """Handle collision between pieces of the same color."""
        # Keep stationary pieces, block moving pieces
        stationary_pieces = [p for p in same_color_pieces if not p.current_state.physics.is_moving and p.current_state.state not in ["move", "jump"]]
        moving_pieces = [p for p in same_color_pieces if p.current_state.physics.is_moving or p.current_state.state in ["move", "jump"]]
        
        if stationary_pieces and moving_pieces:
            # Block moving pieces
            for moving_piece in moving_pieces:
                self._block_piece_movement(moving_piece)
        elif len(same_color_pieces) > 1:
            # Block all but the first piece
            for p in same_color_pieces[1:]:
                self._block_piece_movement(p)

    def _block_piece_movement(self, piece):
        """Block a piece's movement and return it to idle."""
        piece.current_state.physics.target_cell = piece.current_state.physics.current_cell
        piece.current_state.physics.is_moving = False
        now = self.game_time_ms()
        idle_cmd = Command(timestamp=now, piece_id=piece.piece_id, type="idle", params=[])
        piece.on_command(idle_cmd, now)

    def _handle_enemy_collision(self, pieces_in_cell, to_remove):
        """Handle collision between pieces of different colors."""
        # Find attacker (moving piece) vs defender (stationary piece)
        attacking_piece = None
        defending_piece = None
        
        for piece in pieces_in_cell:
            if (piece.current_state.physics.is_moving or 
                piece.current_state.state in ["move", "jump"]):
                attacking_piece = piece
            else:
                defending_piece = piece
        
        # If unclear, use most recent action time
        if not attacking_piece and len(pieces_in_cell) >= 2:
            if hasattr(pieces_in_cell[0], 'last_action_time'):
                attacking_piece = max(pieces_in_cell, key=lambda p: getattr(p, 'last_action_time', 0))
                defending_piece = min(pieces_in_cell, key=lambda p: getattr(p, 'last_action_time', 0))
            else:
                attacking_piece, defending_piece = pieces_in_cell[0], pieces_in_cell[1]
        
        # Remove the defender
        if defending_piece and attacking_piece != defending_piece:
            to_remove.append(defending_piece)

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
                    