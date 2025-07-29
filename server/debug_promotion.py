#!/usr/bin/env python3
"""
Debug Promotion System
======================

Quick test to debug why pawn promotion is not working.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from ChessRulesValidator import ChessRulesValidator

def test_promotion_detection():
    """Test if promotion detection works correctly."""
    print("🔍 Testing Pawn Promotion Detection...")
    
    validator = ChessRulesValidator()
    
    # Create mock white pawn at row 1 (about to promote)
    white_pawn = Mock()
    white_pawn.piece_type = "P"
    white_pawn.color = "White"
    
    # Create mock black pawn at row 6 (about to promote)
    black_pawn = Mock()
    black_pawn.piece_type = "P"
    black_pawn.color = "Black"
    
    print("\n📋 Test Cases:")
    
    # White pawn reaching top (row 0) - should promote
    result1 = validator.is_pawn_promotion(white_pawn, (0, 4))
    print(f"  ✅ White pawn to (0,4): {result1} {'✓' if result1 else '✗'}")
    
    # White pawn not at top (row 1) - should not promote  
    result2 = validator.is_pawn_promotion(white_pawn, (1, 4))
    print(f"  ❌ White pawn to (1,4): {result2} {'✗' if not result2 else '✓'}")
    
    # Black pawn reaching bottom (row 7) - should promote
    result3 = validator.is_pawn_promotion(black_pawn, (7, 4))
    print(f"  ✅ Black pawn to (7,4): {result3} {'✓' if result3 else '✗'}")
    
    # Black pawn not at bottom (row 6) - should not promote
    result4 = validator.is_pawn_promotion(black_pawn, (6, 4))
    print(f"  ❌ Black pawn to (6,4): {result4} {'✗' if not result4 else '✓'}")
    
    # Non-pawn piece - should not promote
    queen = Mock()
    queen.piece_type = "Q"
    queen.color = "White"
    result5 = validator.is_pawn_promotion(queen, (0, 4))
    print(f"  ❌ Queen to (0,4): {result5} {'✗' if not result5 else '✓'}")
    
    return all([result1, not result2, result3, not result4, not result5])

if __name__ == "__main__":
    print("🎯 PAWN PROMOTION DEBUG TEST")
    print("=" * 50)
    
    success = test_promotion_detection()
    
    print(f"\n🎮 Result: {'PASS' if success else 'FAIL'}")
    
    if not success:
        print("❌ Promotion detection is broken!")
    else:
        print("✅ Promotion detection works correctly!")
        print("\n💡 The issue might be elsewhere in the promotion flow:")
        print("   1. Check if promotion commands are being created")
        print("   2. Check if promotion commands are being processed")
        print("   3. Check if promotion UI is triggering properly")
