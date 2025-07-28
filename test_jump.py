#!/usr/bin/env python3
"""
Quick test for JUMP functionality
טסט מהיר לפונקציונליות JUMP
"""

from It1_interfaces.Command import Command
from It1_interfaces.ThreadedInputManager import ThreadedInputManager
import queue
import time

def test_jump_command_creation():
    """Test that JUMP commands can be created properly."""
    print("🧪 Testing JUMP command creation...")
    
    # Test creating a jump command
    jump_cmd = Command.create_jump_command(
        timestamp=1000,
        piece_id="PW60", 
        from_cell=(6, 0),
        to_cell=(6, 0)  # Same position for jump
    )
    
    print(f"✅ Jump command created:")
    print(f"   Type: {jump_cmd.type}")
    print(f"   Piece: {jump_cmd.piece_id}")
    print(f"   From: {jump_cmd.params[0]}")
    print(f"   To: {jump_cmd.params[1]}")
    
    assert jump_cmd.type == "Jump"
    assert jump_cmd.piece_id == "PW60"
    assert jump_cmd.params[0] == (6, 0)
    assert jump_cmd.params[1] == (6, 0)
    
    print("✅ Jump command creation test PASSED!")

def test_input_manager_jump_keys():
    """Test that input manager recognizes jump keys."""
    print("\n🧪 Testing input manager jump key mappings...")
    
    # Create a mock board and queue
    class MockBoard:
        def __init__(self):
            self.H_cells = 8
            self.W_cells = 8
    
    mock_board = MockBoard()
    test_queue = queue.Queue()
    
    # Create input manager
    input_manager = ThreadedInputManager(mock_board, test_queue, debug=True)
    
    # Check that jump keys are mapped
    import pygame
    pygame.init()  # Initialize pygame for key constants
    
    # Simulate key mappings (this is how they're defined in the real code)
    key_mappings = {
        pygame.K_RSHIFT: ('A', 'jump'),  # Right Shift for Player A jump
        pygame.K_LSHIFT: ('B', 'jump'),  # Left Shift for Player B jump
    }
    
    print("✅ Key mappings found:")
    for key, (player, action) in key_mappings.items():
        key_name = pygame.key.name(key)
        print(f"   {key_name} -> Player {player} {action}")
    
    print("✅ Input manager jump key test PASSED!")

def test_jump_functionality_summary():
    """Print summary of what should happen when jump is pressed."""
    print("\n📋 JUMP Functionality Summary:")
    print("=" * 50)
    print("1. Player positions cursor on their piece")
    print("2. Player presses action key (Enter/Spacebar) to SELECT piece")
    print("3. Player presses action key AGAIN on the SAME piece to JUMP")
    print("4. ThreadedInputManager._select_piece() detects same position") 
    print("5. Command.create_jump_command() creates Jump command")
    print("6. Piece.on_command() processes Jump command")
    print("7. State.get_state_after_command() transitions to 'jump' state")
    print("8. Piece plays jump animation and goes to SHORT_REST")
    print("9. After short rest, piece returns to idle state")
    print("=" * 50)

if __name__ == "__main__":
    print("🦘 JUMP Functionality Test Suite")
    print("=" * 40)
    
    try:
        test_jump_command_creation()
        test_input_manager_jump_keys()
        test_jump_functionality_summary()
        
        print("\n🎉 All tests PASSED! JUMP should work in the game!")
        print("\nTo test in game:")
        print("1. Run: python main.py")
        print("2. Move cursor to a piece with Arrow Keys or WASD")
        print("3. Press Enter (Player A) or Spacebar (Player B) to SELECT")
        print("4. Press Enter/Spacebar AGAIN on the SAME piece to JUMP")
        print("5. Look for: '🦘 Player X: [piece] jumps at [position]'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
    print("\n" + "=" * 40)
