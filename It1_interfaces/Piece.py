# from .Board import Board
# from .Command import Command
# from .State import State
# import cv2

# class Piece:
#     def __init__(self, piece_id: str, init_state: State, piece_type: str):
#         """Initialize a piece with ID, initial state, and type."""
#         self.piece_id = piece_id
#         self.current_state = init_state
#         self.piece_type = piece_type  # Add piece type
#         self.start_time = 0
        
#         # Cooldown system
#         self.last_action_time = 0
#         self.cooldown_duration = 2000  # 2 seconds in ms
        
#     def on_command(self, cmd: Command, now_ms: int):
#         """Handle a command for this piece."""
#         if cmd.piece_id != self.piece_id:
#             return  # Command not for this piece
        
#         # Check cooldown
#         if now_ms - self.last_action_time < self.cooldown_duration:
#             return  # Still in cooldown
            
#         # Process command and potentially transition state
#         new_state = self.current_state.get_state_after_command(cmd, now_ms)
#         if new_state != self.current_state:
#             print(f"[DEBUG] Piece {self.piece_id} transitioning to state: {new_state.state}")
#             self.current_state = new_state
#             self.last_action_time = now_ms
        
#         self.current_state.physics.reset(cmd)

#     def reset(self, start_ms: int):
#         self.start_time = start_ms
#         self.last_action_time = start_ms  # לשים לב לסנכרן עם זמן המשחק
#         idle_cmd = Command.create_idle_command(start_ms, self.piece_id)
#         self.current_state.reset(idle_cmd)

#     def update(self, now_ms: int):
#         """Update the piece state based on current time."""
#         new_state = self.current_state.update(now_ms)
#         if new_state != self.current_state:
#             self.current_state = new_state
#         # print(f"[INFO] Piece {self.piece_id} is in state: {self.current_state.state}")

#     def draw_on_board(self, board: Board, now_ms: int):
#         """Draw the piece on the board with cooldown overlay (yellow fading)."""
#         sprite = self.current_state.graphics.get_img()
#         x, y = self.current_state.physics.get_pos()

#         try:
#             sprite.draw_on(board.img, x, y)

#             remaining_cooldown = self.cooldown_duration - (now_ms - self.last_action_time)
#             if remaining_cooldown > 0:
#                 cooldown_ratio = remaining_cooldown / self.cooldown_duration
#                 import numpy as np
#                 overlay_height = int(board.cell_H_pix * cooldown_ratio)
#                 if overlay_height > 0 and board.img.img is not None:
#                     h, w = board.img.img.shape[:2]
#                     if y + overlay_height <= h and x + board.cell_W_pix <= w:
#                         overlay = board.img.img[y:y + overlay_height, x:x + board.cell_W_pix].copy()
#                         yellow_overlay = np.full_like(overlay, (0, 255, 255))  # Yellow in BGR
#                         alpha = 0.5
#                         blended = cv2.addWeighted(yellow_overlay, alpha, overlay, 1 - alpha, 0)
#                         board.img.img[y:y + overlay_height, x:x + board.cell_W_pix] = blended
#         except Exception:
#             pass  # Error message suppressed


# תיקון לשיטת draw_on_board ב-Piece.py
from .Board import Board
from .Command import Command
from .State import State
import cv2

class Piece:
    def __init__(self, piece_id: str, init_state: State, piece_type: str):
        """Initialize a piece with ID, initial state, and type."""
        self.piece_id = piece_id
        self.current_state = init_state
        self.piece_type = piece_type
        self.start_time = 0
        
        # Cooldown system
        self.last_action_time = 0
        self.cooldown_duration = 2000  # 2 seconds in ms
        
        print(f"[DEBUG] Piece {piece_id} created with initial state: {init_state.state}")
        
    def on_command(self, cmd: Command, now_ms: int):
        """Handle a command for this piece."""
        if cmd.piece_id != self.piece_id:
            return  # Command not for this piece
        
        print(f"[DEBUG] Piece {self.piece_id} received command: {cmd.type} in state: {self.current_state.state}")
        
        # Check cooldown
        if now_ms - self.last_action_time < self.cooldown_duration:
            print(f"[DEBUG] Piece {self.piece_id} is in cooldown, ignoring command")
            return  # Still in cooldown
            
        # Process command and potentially transition state
        old_state = self.current_state.state
        new_state = self.current_state.get_state_after_command(cmd, now_ms)
        
        if new_state != self.current_state:
            print(f"[DEBUG] Piece {self.piece_id} transitioning from '{old_state}' to '{new_state.state}'")
            self.current_state = new_state
            self.last_action_time = now_ms
        else:
            print(f"[DEBUG] Piece {self.piece_id} staying in state '{old_state}' (no transition found)")
        
        # Reset physics for the current state (whether it changed or not)
        self.current_state.physics.reset(cmd)

    def reset(self, start_ms: int):
        self.start_time = start_ms
        self.last_action_time = start_ms
        idle_cmd = Command.create_idle_command(start_ms, self.piece_id)
        self.current_state.reset(idle_cmd)

    def update(self, now_ms: int):
        """Update the piece state based on current time."""
        old_state_name = self.current_state.state
        new_state = self.current_state.update(now_ms)
        
        if new_state != self.current_state:
            print(f"[DEBUG] Piece {self.piece_id} auto-transitioned from '{old_state_name}' to '{new_state.state}'")
            self.current_state = new_state

    def draw_on_board(self, board: Board, now_ms: int):
        """Draw the piece on the board with cooldown overlay (yellow fading)."""
        sprite = self.current_state.graphics.get_img()
        x, y = self.current_state.physics.get_pos(now_ms)  # ❗ העברת now_ms

        try:
            sprite.draw_on(board.img, x, y)

            remaining_cooldown = self.cooldown_duration - (now_ms - self.last_action_time)
            if remaining_cooldown > 0:
                cooldown_ratio = remaining_cooldown / self.cooldown_duration
                import numpy as np
                overlay_height = int(board.cell_H_pix * cooldown_ratio)
                if overlay_height > 0 and board.img.img is not None:
                    h, w = board.img.img.shape[:2]
                    if y + overlay_height <= h and x + board.cell_W_pix <= w:
                        overlay = board.img.img[y:y + overlay_height, x:x + board.cell_W_pix].copy()
                        yellow_overlay = np.full_like(overlay, (0, 255, 255))  # Yellow in BGR
                        alpha = 0.5
                        blended = cv2.addWeighted(yellow_overlay, alpha, overlay, 1 - alpha, 0)
                        board.img.img[y:y + overlay_height, x:x + board.cell_W_pix] = blended
        except Exception:
            pass  # Error message suppressed