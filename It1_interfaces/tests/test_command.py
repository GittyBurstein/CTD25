#!/usr/bin/env python3
"""
🧪 מקיף של טסטים למחלקת Command
"""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Command import Command


class TestCommand(unittest.TestCase):
    """טסטים מקיפים למחלקת Command"""
    
    def setUp(self):
        """הכנת נתונים לכל טסט"""
        self.timestamp = 1000
        self.piece_id = "NW71"
        self.from_cell = (0, 1)
        self.to_cell = (2, 2)
    
    def test_command_creation(self):
        """🧪 טסט יצירת פקודה בסיסית"""
        cmd = Command(
            timestamp=self.timestamp,
            piece_id=self.piece_id,
            type="Move",
            params=[self.from_cell, self.to_cell]
        )
        
        self.assertEqual(cmd.timestamp, self.timestamp)
        self.assertEqual(cmd.piece_id, self.piece_id)
        self.assertEqual(cmd.type, "Move")
        self.assertEqual(cmd.params, [self.from_cell, self.to_cell])
    
    def test_post_init_params_validation(self):
        """🧪 טסט תיקון params שאינם רשימה"""
        # Create command with non-list params
        cmd = Command(
            timestamp=self.timestamp,
            piece_id=self.piece_id,
            type="Move",
            params="invalid"  # Not a list!
        )
        
        # Should be converted to empty list
        self.assertEqual(cmd.params, [])
    
    def test_create_move_command(self):
        """🧪 טסט factory method לפקודת תנועה"""
        cmd = Command.create_move_command(
            timestamp=self.timestamp,
            piece_id=self.piece_id,
            from_cell=self.from_cell,
            to_cell=self.to_cell
        )
        
        self.assertEqual(cmd.timestamp, self.timestamp)
        self.assertEqual(cmd.piece_id, self.piece_id)
        self.assertEqual(cmd.type, "Move")
        self.assertEqual(cmd.params, [self.from_cell, self.to_cell])
    
    def test_create_jump_command(self):
        """🧪 טסט factory method לפקודת קפיצה"""
        cmd = Command.create_jump_command(
            timestamp=self.timestamp,
            piece_id=self.piece_id,
            from_cell=self.from_cell,
            to_cell=self.to_cell
        )
        
        self.assertEqual(cmd.timestamp, self.timestamp)
        self.assertEqual(cmd.piece_id, self.piece_id)
        self.assertEqual(cmd.type, "Jump")
        self.assertEqual(cmd.params, [self.from_cell, self.to_cell])
    
    def test_create_idle_command(self):
        """🧪 טסט factory method לפקודת המתנה"""
        cmd = Command.create_idle_command(
            timestamp=self.timestamp,
            piece_id=self.piece_id
        )
        
        self.assertEqual(cmd.timestamp, self.timestamp)
        self.assertEqual(cmd.piece_id, self.piece_id)
        self.assertEqual(cmd.type, "idle")
        self.assertEqual(cmd.params, [])
    
    def test_get_source_cell(self):
        """🧪 טסט קבלת תא המקור"""
        # Test valid source cell
        cmd = Command.create_move_command(
            self.timestamp, self.piece_id, self.from_cell, self.to_cell
        )
        self.assertEqual(cmd.get_source_cell(), self.from_cell)
        
        # Test empty params
        empty_cmd = Command.create_idle_command(self.timestamp, self.piece_id)
        self.assertIsNone(empty_cmd.get_source_cell())
        
        # Test invalid params
        invalid_cmd = Command(self.timestamp, self.piece_id, "test", ["invalid"])
        self.assertIsNone(invalid_cmd.get_source_cell())
    
    def test_get_target_cell(self):
        """🧪 טסט קבלת תא היעד"""
        # Test valid target cell
        cmd = Command.create_move_command(
            self.timestamp, self.piece_id, self.from_cell, self.to_cell
        )
        self.assertEqual(cmd.get_target_cell(), self.to_cell)
        
        # Test single param (no target)
        single_param_cmd = Command(self.timestamp, self.piece_id, "test", [self.from_cell])
        self.assertIsNone(single_param_cmd.get_target_cell())
        
        # Test empty params
        empty_cmd = Command.create_idle_command(self.timestamp, self.piece_id)
        self.assertIsNone(empty_cmd.get_target_cell())
    
    def test_str_representation(self):
        """🧪 טסט ייצוג מחרוזת של הפקודה"""
        cmd = Command.create_move_command(
            self.timestamp, self.piece_id, self.from_cell, self.to_cell
        )
        
        expected = f"Command(Move, {self.piece_id}, {[self.from_cell, self.to_cell]})"
        self.assertEqual(str(cmd), expected)
    
    def test_command_types(self):
        """🧪 טסט סוגי פקודות שונים"""
        test_cases = [
            ("Move", [self.from_cell, self.to_cell]),
            ("Jump", [self.from_cell, self.to_cell]),
            ("Attack", [self.from_cell, self.to_cell]),
            ("idle", []),
            ("complete", [])
        ]
        
        for cmd_type, params in test_cases:
            with self.subTest(cmd_type=cmd_type):
                cmd = Command(self.timestamp, self.piece_id, cmd_type, params)
                self.assertEqual(cmd.type, cmd_type)
                self.assertEqual(cmd.params, params)
    
    def test_edge_cases(self):
        """🧪 טסט מקרי קיצון"""
        # Test with zero timestamp
        cmd = Command(0, self.piece_id, "Move", [])
        self.assertEqual(cmd.timestamp, 0)
        
        # Test with empty piece_id
        cmd = Command(self.timestamp, "", "Move", [])
        self.assertEqual(cmd.piece_id, "")
        
        # Test with special characters in piece_id
        special_id = "NW71@#$%"
        cmd = Command(self.timestamp, special_id, "Move", [])
        self.assertEqual(cmd.piece_id, special_id)
        
        # Test with None as params (should be converted to [])
        cmd = Command(self.timestamp, self.piece_id, "Move", None)
        self.assertEqual(cmd.params, [])


if __name__ == '__main__':
    print("🧪 הרצת טסטים למחלקת Command...")
    unittest.main(verbosity=2)
