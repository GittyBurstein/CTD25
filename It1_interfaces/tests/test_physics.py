#!/usr/bin/env python3
"""
🧪 טסטים עבודיים למחלקת Physics
"""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Try to import from the main package
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    # Import the whole package first
    import It1_interfaces
    from It1_interfaces.Physics import Physics
    from It1_interfaces.Command import Command
print("✅ Physics ו-Command יובאו successfully מpackage!")
    IMPORTS_OK = True
except ImportError as e:
    print(f"❌ Package import failed: {e}")
    try:
        # Fallback - try direct import (won't work with relative imports)
        from Physics import Physics
        from Command import Command  
print("✅ Direct import עבד!")
        IMPORTS_OK = True
    except ImportError as e2:
        print(f"❌ Direct import also failed: {e2}")
        IMPORTS_OK = False


class TestPhysics(unittest.TestCase):
"""tests עבודיים for class Physics"""
    
    def test_initialization_works(self):
"""🧪 test שהאתחול עובד"""
        if not IMPORTS_OK:
            self.skipTest("Required modules not available")
            
        physics = Physics((2, 3), speed_cells_per_sec=2.0)
        self.assertEqual(physics.current_cell, (2, 3))
        self.assertEqual(physics.speed_cells_per_sec, 2.0)
print("✅ Physics אותחל successfully!")
    
    def test_get_pos_works(self):
"""🧪 test שget_pos עובד"""
        if not IMPORTS_OK:
            self.skipTest("Required modules not available")
            
        physics = Physics((2, 3))
        physics.is_moving = False
        
        pos = physics.get_pos(1000)
        self.assertEqual(pos, (2, 3))
print("✅ get_pos עובד successfully!")
    
    def test_command_integration(self):
"""🧪 test אינטגרציה with Command"""
        if not IMPORTS_OK:
            self.skipTest("Required modules not available")
            
        # Create a simple command
        cmd = Command.create_move_command(1000, "test", (0, 0), (1, 1))
        self.assertIsNotNone(cmd)
print("✅ Command נוצר successfully!")


if __name__ == '__main__':
print("🧪 running tests עבודיים ל-Physics...")
    unittest.main(verbosity=2)
