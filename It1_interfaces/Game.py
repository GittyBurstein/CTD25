import inspect
import pathlib
import queue, threading, time, cv2, math
from typing import List, Dict, Tuple, Optional
from It1_interfaces.Board import Board
from It1_interfaces.Command import Command
from It1_interfaces.Piece import Piece
from It1_interfaces.img import Img


class InvalidBoard(Exception): ...
# ────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, pieces: List[Piece], board: Board):
        """Initialize the game with pieces, board, and optional event bus."""
        self.pieces = {p.piece_id: p for p in pieces}
        self.board = board
        self.start_time = time.time()
        self.user_input_queue = queue.Queue()

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
        print("[DEBUG] Drawing all pieces on the board...")
        board_img = self.clone_board().img
        for piece in self.pieces.values():
            piece.draw_on_board(board_img, self.game_time_ms())
            print(f"[DEBUG] Drawing piece {piece.piece_id} on the board...")
        self.current_display = board_img

    def start_user_input_thread(self):
        """Start the user input thread for mouse handling."""
        def input_worker():
            while True:
                # Handle user input here (e.g., from keyboard or mouse)
                pass

        thread = threading.Thread(target=input_worker, daemon=True)
        thread.start()

    # ─── main public entrypoint ──────────────────────────────────────────────
    def run(self):
        """Main game loop."""
        print("-----[DEBUG] Entering run()...")
        self.start_user_input_thread()

        start_ms = self.game_time_ms()
        for p in self.pieces.values():
            p.reset(start_ms)

        # ─────── main loop ──────────────────────────────────────────────────
        while not self._is_win():
            now = self.game_time_ms()

            # (1) Update physics & animations
            for p in self.pieces.values():
                p.update(now)

            # (2) Handle queued Commands from input thread
            while not self.user_input_queue.empty():
                cmd: Command = self.user_input_queue.get()
                self._process_input(cmd)

            # (3) Draw current position
            print("XXX[DEBUG] Entering _draw function...")
            self._draw()
            if not self._show():  # Returns False if user closed window
                break

            # (4) Detect captures
            self._resolve_collisions()

        self._announce_win()
        cv2.destroyAllWindows()

    # ─── drawing helpers ────────────────────────────────────────────────────
    def _process_input(self, cmd: Command):
        """Process player input commands."""
        if cmd.piece_id in self.pieces:
            self.pieces[cmd.piece_id].on_command(cmd)

    

    def _show(self) -> bool:
        """Show the current frame and handle window events."""
        if hasattr(self, 'current_display'):
            cv2.imshow("Kung Fu Chess", self.current_display.img)
            return cv2.waitKey(1) & 0xFF != 27  # Return False if ESC pressed
        return True

    # ─── capture resolution ────────────────────────────────────────────────
    def _resolve_collisions(self):
        """Resolve piece collisions and captures."""
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
                survivor = pieces_in_cell[0]
                for p in pieces_in_cell[1:]:
                    to_remove.append(p)

        # Remove captured pieces
        for p in to_remove:
            del self.pieces[p.piece_id]

    # ─── board validation & win detection ───────────────────────────────────
    def _is_win(self) -> bool:
        """Check if the game has ended."""
        kings = [p for p in self.pieces.values() if p.piece_type == "King"]
        print(f"????[DEBUG] Number of kings remaining: {len(kings)}")
        return False  # Temporary override to allow the game to continue

    def _announce_win(self):
        """Announce the winner."""
        kings = [p for p in self.pieces.values() if p.piece_type == "King"]
        if len(kings) == 1:
            print(f"Game Over! {kings[0].color} wins!")
        else:
            print("Game Over! It's a draw.")
        print("Game Over! Press any key to close the window.")
        cv2.waitKey(0)  # Wait for a key press before closing the window
