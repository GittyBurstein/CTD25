#!/usr/bin/env python3
"""
🧪 טסט לגרסאות המקוצרות
"""

# חיבור הקובץ main with הגרסאות המקוצרות
def main():
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
    from It1_interfaces.EventBus import EventBus
    from It1_interfaces.SoundManager import SoundManager
    from It1_interfaces.AnimationManager import AnimationManager
    import pathlib

# גרסאות מקוצרות!!!
    from It1_interfaces.MoveLogger_short import MoveLogger
    from It1_interfaces.ScoreManager_short import ScoreManager
    
# initialization
    event_bus = EventBus()
    sound_manager = SoundManager()
    score_manager = ScoreManager()
    move_logger = MoveLogger()
    animation_manager = AnimationManager()

# מנויים
    from It1_interfaces.EventTypes import MOVE_DONE, PIECE_CAPTURED, GAME_STARTED, GAME_ENDED
    event_bus.subscribe(MOVE_DONE, sound_manager)
    event_bus.subscribe(PIECE_CAPTURED, sound_manager)
    event_bus.subscribe(GAME_STARTED, sound_manager)
    event_bus.subscribe(GAME_ENDED, sound_manager)
    event_bus.subscribe(MOVE_DONE, score_manager)
    event_bus.subscribe(PIECE_CAPTURED, score_manager)
    event_bus.subscribe(MOVE_DONE, move_logger)
    event_bus.subscribe(GAME_STARTED, animation_manager)
    event_bus.subscribe(GAME_ENDED, animation_manager)

# rest of code identical to original...
# [This code is for testing only - no need to run it]

if __name__ == "__main__":
print("This is a test file only")
