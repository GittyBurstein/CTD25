import sys
import os
import pathlib

# הוספת נתיב תיקיית It1_interfaces
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
game_dir = os.path.join(parent_dir, "It1_interfaces")
sys.path.append(game_dir)

from Game import Game
from PieceFactory import PieceFactory
from Board import Board
from img import Img

def load_board_from_csv(path: pathlib.Path) -> Board:
    with open(path) as f:
        lines = [line.strip().split(",") for line in f if line.strip()]
    rows = len(lines)
    cols = len(lines[0])
    background = Img().read(r"C:\Users\1\Desktop\ShachMat\CTD25\board.png", size=(cols * 64, rows * 64))
    return Board(
        cell_H_pix=64,
        cell_W_pix=64,
        cell_H_m=1,
        cell_W_m=1,
        W_cells=cols,
        H_cells=rows,
        img=background
    )

if __name__ == "__main__":
    print("Initializing Game...")
    base_path = pathlib.Path(__file__).parent.parent
    board_path = base_path / "pieces" / "board.csv"
    pieces_path = base_path / "pieces"

    board = load_board_from_csv(board_path)
    factory = PieceFactory(pieces_path, board, (board.H_cells, board.W_cells))

    pieces = []
    pawn_count = {"PW": 8, "PB": 8, "RW": 2, "RB": 2, "NW": 2, "NB": 2, "BW": 2, "BB": 2}

    for piece_dir in pieces_path.iterdir():
        if piece_dir.is_dir():
            piece_id = piece_dir.name

            if piece_id in pawn_count:
                for i in range(pawn_count[piece_id]):
                    full_id = f"{piece_id}{i}"
                    print(f"[DEBUG] Creating {full_id} from folder: {piece_dir}")
                    pieces.append(factory.create(piece_dir, full_id, i))
            else:
                print(f"[DEBUG] Creating {piece_id} from folder: {piece_dir}")
                pieces.append(factory.create(piece_dir, piece_id))

    for p in pieces:
        print("Loaded piece:", p.piece_id)

    game = Game(pieces, board)
    print("Game initialized successfully!")
    print("Starting game loop...")
    game.run()
