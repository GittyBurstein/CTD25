import csv
import os
from It1_interfaces.Game import Game
from It1_interfaces.Board import Board
from It1_interfaces.Piece import Piece
from It1_interfaces.Moves import Moves
from It1_interfaces.Graphics import Graphics
from It1_interfaces.Physics import Physics
from It1_interfaces.State import State
from It1_interfaces.img import Img
import pathlib
import cv2

# Initialize the board image
board_img = Img()
print(f"[DEBUG] Board image loaded: {board_img.img is not None}")
print(f"[DEBUG] Loading board image from: {pathlib.Path('board.png').resolve()}")
print("[DEBUG] Attempting to read the image using Img.read...")
print(f"[DEBUG] Path exists: {pathlib.Path('board.png').exists()}")
board_img.read(pathlib.Path("board.png"), size=(512, 512))

if board_img.img is None:
    print("[ERROR] Failed to load the board image. Please check the file format and path.")
    exit(1)  # Exit if the image is not loaded

# Directly attempt to load the image using OpenCV
cv2_img = cv2.imread(str(pathlib.Path("board.png")))
if cv2_img is None:
    print("[ERROR] OpenCV failed to load the image. Please check the file format and path.")
    exit(1)  # Exit if OpenCV fails to load the image
else:
    print("[DEBUG] OpenCV successfully loaded the image.")

# Initialize the board
board = Board(cell_H_pix=64, cell_W_pix=64, W_cells=8, H_cells=8, img=board_img)

# Load initial positions from board.csv
pieces = []
board_csv_path = os.path.join(os.path.dirname(__file__), "pieces", "board.csv")
if not os.path.exists(board_csv_path):
    print(f"[ERROR] The board.csv file was not found at {board_csv_path}. Please ensure the file exists.")
    exit(1)  # Exit if the CSV file is missing

# Debug: Print each cell being processed from the CSV
print("[DEBUG] Processing board.csv:")
with open(board_csv_path, "r") as file:
    reader = csv.reader(file)
    for row_idx, row in enumerate(reader):
        for col_idx, cell in enumerate(row):
            print(f"[DEBUG] Cell[{row_idx}][{col_idx}]: {cell}")  # Debug: Print cell content
            if cell:  # If the cell is not empty
                # Debug: Validate cell content and piece type
                if len(cell) < 2:
                    print(f"[ERROR] Invalid cell format at [{row_idx}][{col_idx}]: '{cell}'")
                    continue

                # Debug: Log the full cell content for better clarity
                print(f"[DEBUG] Full cell content: '{cell}' at [{row_idx}][{col_idx}]")

                # Improved piece type detection logic
                if len(cell) == 2:
                    color_char, piece_type = cell[0], cell[1]  # First character for color, second for type
                    if piece_type == 'K':
                        print(f"[DEBUG] King detected at [{row_idx}][{col_idx}] with color {color_char}")
                else:
                    print(f"[ERROR] Unexpected cell format at [{row_idx}][{col_idx}]: '{cell}'")
                    continue

                print(f"[DEBUG] Detected piece type: {piece_type} at [{row_idx}][{col_idx}] with color {color_char}")

                color = "White" if cell[0] == "W" else "Black"
                piece_id = f"{cell}{row_idx}{col_idx}"

                # Initialize Moves, Graphics, and Physics
                moves_path = pathlib.Path(f"pieces/{cell}/moves.txt")
                sprites_folder = pathlib.Path(f"pieces/{cell}/states/idle/sprites")
                moves = Moves(moves_path, dims=(8, 8))
                graphics = Graphics(sprites_folder, cell_size=(64, 64))
                physics = Physics(start_cell=(row_idx, col_idx), board=board)

                # Create State and Piece
                state = State(moves, graphics, physics)
                pieces.append(Piece(piece_id=piece_id, init_state=state, piece_type=piece_type))

                # Ensure piece_type is correctly assigned and kings are added properly
                if piece_type == 'K':
                    print(f"[DEBUG] Adding King to pieces list: {piece_id}")
                else:
                    print(f"[DEBUG] Adding piece to pieces list: {piece_id}, Type: {piece_type}")

                # Correct piece_type assignment for kings
                if piece_type == 'K':
                    print(f"[DEBUG] Confirming King type before creating Piece: {piece_id}")
                else:
                    print(f"[DEBUG] Confirming piece type before creating Piece: {piece_id}, Type: {piece_type}")

# Debug: Print the loaded pieces
print("[DEBUG] Loaded pieces:")
for piece in pieces:
    print(f"[DEBUG] Piece ID: {piece.piece_id}, Type: {piece.piece_type}, Initial Position: {piece.current_state.physics.get_pos()}")

# Debug: Check if kings are initialized correctly
king_count = sum(1 for piece in pieces if piece.piece_type == 'K')
if king_count != 2:
    print(f"[ERROR] Incorrect number of kings initialized: {king_count}. Expected: 2.")
    exit(1)  # Exit if the number of kings is incorrect
else:
    print(f"[DEBUG] Number of kings initialized correctly: {king_count}")

# Create the game instance
game = Game(pieces=pieces, board=board)

# Show the board image after drawing pieces to verify rendering
board_img.show("Board with Pieces")

# Debug: Log before showing the board image
print("[DEBUG] Attempting to show the board image...")

# Use OpenCV to display the image directly
cv2.imshow("Board with Pieces", cv2_img)
cv2.waitKey(0)  # Wait for a key press to close the window
cv2.destroyAllWindows()  # Close the OpenCV window

# Debug: Log after showing the board image
print("[DEBUG] Board image displayed successfully.")

if __name__ == "__main__":
    game.run()
