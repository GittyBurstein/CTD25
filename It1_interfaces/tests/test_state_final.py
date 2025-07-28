#!/usr/bin/env python3
"""
🧪 טסטים מקיפים למחלקת State - עובד עם module system
כיסוי מלא של פונקציונליות State עם 50+ טסטים
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import pathlib
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from State import (
        State, 
        extract_piece_type_from_sprites_path,
        construct_sprites_path_for_state,
        create_long_rest_state,
        create_short_rest_state,
        create_move_state
    )
    from Command import Command
    from Moves import Moves
    from Graphics import Graphics
    from Physics import Physics
    HAS_IMPORTS = True
print("✅ all הimports הצליחו!")
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    HAS_IMPORTS = False

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateHelperFunctions(unittest.TestCase):
"""🔧 tests comprehensive לפונקציות עזר"""
    
    def test_extract_piece_type_string_paths(self):
"""🧪 חילוץ סוג piece מנתיבי string"""
        test_cases = [
            ("pieces/PW/states/idle/sprites", "PW"),
            ("pieces/BB/states/move/sprites", "BB"), 
            ("pieces/KW/states/jump/sprites", "KW"),
            ("pieces/QB/states/long_rest/sprites", "QB"),
            ("pieces/NB/states/short_rest/sprites", "NB"),
            ("pieces/RW/states/attack/sprites", "RW"),
        ]
        
        for path, expected in test_cases:
            with self.subTest(path=path):
                result = extract_piece_type_from_sprites_path(path)
                self.assertEqual(result, expected)
        
    def test_extract_piece_type_pathlib_objects(self):
"""🧪 חילוץ סוג piece מאובייקטי pathlib"""
        path = pathlib.Path("pieces/RB/states/defend/sprites")
        result = extract_piece_type_from_sprites_path(path)
        self.assertEqual(result, "RB")
        
    def test_extract_piece_type_invalid_structures(self):
"""🧪 paths no תקינים צריכים להחזיר None"""
        invalid_paths = [
            "invalid/path/structure",
            "pieces/PW",  # חסר states
            "pieces/PW/states",  # חסר state name
            "pieces/states/idle/sprites",  # חסר piece type
            "wrong/PW/states/idle/sprites",  # לא מתחיל ב-pieces
            "",  # ריק
            "sprites",  # רק sprites
            "pieces/PW/wrong/idle/sprites",  # states שגוי
        ]
        
        for path in invalid_paths:
            with self.subTest(path=path):
                result = extract_piece_type_from_sprites_path(path)
                self.assertIsNone(result)
                
    def test_construct_sprites_path_valid_cases(self):
"""🧪 בניית נתיבי sprites תקינים"""
        test_cases = [
            ("pieces/PW/states/idle/sprites", "move", "pieces/PW/states/move/sprites"),
            ("pieces/BB/states/jump/sprites", "idle", "pieces/BB/states/idle/sprites"),
            ("pieces/KW/states/long_rest/sprites", "short_rest", "pieces/KW/states/short_rest/sprites"),
            ("pieces/QB/states/attack/sprites", "defend", "pieces/QB/states/defend/sprites"),
        ]
        
        for current_path, target_state, expected_str in test_cases:
            with self.subTest(current=current_path, target=target_state):
                result = construct_sprites_path_for_state(current_path, target_state)
                expected = pathlib.Path(expected_str)
                self.assertEqual(result, expected)
                
    def test_construct_sprites_path_fallback(self):
"""🧪 fallback לנתיב מקורי כשלא ניתן לחלץ"""
        invalid_path = "invalid/structure/here"
        target_state = "any_state"
        result = construct_sprites_path_for_state(invalid_path, target_state)
        self.assertEqual(result, invalid_path)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateInitialization(unittest.TestCase):
"""🏗️ tests comprehensive לinitialize State"""
    
    def setUp(self):
"""🔧 setup mock objects"""
        self.mock_moves = Mock(spec=Moves)
        
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.sprites_folder = "pieces/PW/states/idle/sprites"
        self.mock_graphics.cell_size = 64
        self.mock_graphics.state_name = "idle"
        self.mock_graphics.copy.return_value = self.mock_graphics
        self.mock_graphics.reset = Mock()
        self.mock_graphics.update = Mock()
        
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.current_cell = (0, 0)
        self.mock_physics.target_cell = (1, 1)
        self.mock_physics.is_moving = False
        self.mock_physics.copy.return_value = self.mock_physics
        self.mock_physics.reset = Mock()
        self.mock_physics.update = Mock(return_value=False)
        
    def test_default_initialization(self):
"""🧪 initialization with ברירת מחדל"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
# checking all המאפיינים הבסיסיים
        self.assertEqual(state.moves, self.mock_moves)
        self.assertEqual(state.graphics, self.mock_graphics)
        self.assertEqual(state.physics, self.mock_physics)
        self.assertEqual(state.state, "idle")  # ברירת מחדל
        self.assertEqual(state.transitions, {})
        self.assertEqual(state.state_start_time, 0)
        self.assertIsNone(state.current_command)
        self.assertFalse(state.is_rest_state)
        self.assertEqual(state.rest_duration_ms, 0)
        
    def test_custom_state_names(self):
"""🧪 initialization with שמות state מותאמים אישית"""
        custom_states = [
            "move", "jump", "attack", "defend", 
            "long_rest", "short_rest", "special",
            "custom_action", "waiting", "preparing"
        ]
        
        for state_name in custom_states:
            with self.subTest(state_name=state_name):
                state = State(self.mock_moves, self.mock_graphics, self.mock_physics, state_name)
                self.assertEqual(state.state, state_name)
# checking שאר המאפיינים נשארים identical
                self.assertEqual(state.moves, self.mock_moves)
                self.assertEqual(state.graphics, self.mock_graphics)
                self.assertEqual(state.physics, self.mock_physics)
                
    def test_object_types_validation(self):
"""🧪 checking טיפוסי האובייקטים שנוצרו"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "test")
        
# checking טיפוסים
        self.assertIsInstance(state.transitions, dict)
        self.assertIsInstance(state.state_start_time, int)
        self.assertIsInstance(state.is_rest_state, bool)
        self.assertIsInstance(state.rest_duration_ms, int)
        self.assertIsInstance(state.state, str)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateCopyFunctionality(unittest.TestCase):
"""📋 tests comprehensive לפונקציונליות copy"""
    
    def setUp(self):
"""🔧 setup data"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.state_name = "idle"
        self.mock_graphics.copy.return_value = self.mock_graphics
        
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.copy.return_value = self.mock_physics
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "test_state")
        
    def test_copy_preserves_basic_properties(self):
"""🧪 copy משמר מאפיינים basic"""
# הגדרת מאפיינים מיוחדים
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 2500
        
        copied_state = self.state.copy()
        
# checking שכל המאפיינים הועתקו
        self.assertEqual(copied_state.state, self.state.state)
        self.assertEqual(copied_state.is_rest_state, self.state.is_rest_state)
        self.assertEqual(copied_state.rest_duration_ms, self.state.rest_duration_ms)
        self.assertEqual(copied_state.moves, self.state.moves)  # אותו reference
        
    def test_copy_calls_component_methods(self):
"""🧪 copy קורא לmethods of components"""
        copied_state = self.state.copy()
        
# checking שcopy נקרא על all component
        self.mock_graphics.copy.assert_called_once()
        self.mock_physics.copy.assert_called_once()
        
    def test_copy_resets_transitions(self):
"""🧪 copy מאפס the הtransitions"""
# הוספת transitions למקור
        target_state = Mock()
        self.state.set_transition("test_event", target_state)
        self.state.set_transition("another_event", target_state)
        
        copied_state = self.state.copy()
        
# Transitions צריכים להיות empty בהעתק
        self.assertEqual(copied_state.transitions, {})
        self.assertNotEqual(len(copied_state.transitions), len(self.state.transitions))
        
    def test_copy_fixes_graphics_state_name(self):
"""🧪 copy מתקן the state_name בgraphics"""
        copied_state = self.state.copy()
        
# checking שstate_name הוגדר נכון
        self.assertEqual(copied_state.graphics.state_name, self.state.state)
        
    def test_multiple_copies_independence(self):
"""🧪 number copies עצמאיים זה מזה"""
        copy1 = self.state.copy()
        copy2 = self.state.copy()
        copy3 = copy1.copy()
        
# all copy צריך להיות אובייקט נפרד
        copies = [copy1, copy2, copy3]
        for i, copy_a in enumerate(copies):
            for j, copy_b in enumerate(copies):
                if i != j:
                    self.assertNotEqual(copy_a, copy_b)
                    
# but with אותם מאפיינים
        for copy_state in copies:
            self.assertEqual(copy_state.state, self.state.state)
            self.assertEqual(copy_state.is_rest_state, self.state.is_rest_state)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateTransitions(unittest.TestCase):
"""🔄 tests comprehensive לטrנzition logic"""
    
    def setUp(self):
"""🔧 setup data"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_physics = Mock(spec=Physics)
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
    def test_single_transition_setup(self):
"""🧪 הגדרת transition יחיד"""
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        
        self.state.set_transition("move_command", target_state)
        
# checking שהtransition נוסף נכון
        self.assertEqual(self.state.transitions["move_command"], target_state)
        self.assertEqual(len(self.state.transitions), 1)
        
    def test_multiple_transitions_setup(self):
"""🧪 הגדרת transitions מרובים"""
        move_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        jump_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "jump")
        attack_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "attack")
        rest_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "rest")
        
        transitions_map = {
            "move": move_state,
            "jump": jump_state,
            "attack": attack_state,
            "rest": rest_state,
            "complete": move_state,
            "timeout": rest_state
        }
        
# הוספת all הtransitions
        for event, target in transitions_map.items():
            self.state.set_transition(event, target)
            
# checking שכולם נוספו נכון
        self.assertEqual(len(self.state.transitions), 6)
        for event, target in transitions_map.items():
            self.assertEqual(self.state.transitions[event], target)
            
    def test_transition_overwriting(self):
"""🧪 דריסת transitions קיימים"""
        state1 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "state1")
        state2 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "state2")
        state3 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "state3")
        
# הוספה first
        self.state.set_transition("event", state1)
        self.assertEqual(self.state.transitions["event"], state1)
        
# דריסה first
        self.state.set_transition("event", state2)
        self.assertEqual(self.state.transitions["event"], state2)
        
# דריסה שנייה
        self.state.set_transition("event", state3)
        self.assertEqual(self.state.transitions["event"], state3)
        
# עדיין only transition one
        self.assertEqual(len(self.state.transitions), 1)
        
    def test_special_event_names(self):
"""🧪 שמות events מיוחדים"""
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "target")
        
        special_events = [
            "move-with-dash", "jump_with_underscore", "attack.with.dots",
            "complete!", "timeout?", "special@event", "event#1",
            "very_long_event_name_with_many_words"
        ]
        
        for event in special_events:
            with self.subTest(event=event):
                self.state.set_transition(event, target_state)
                self.assertEqual(self.state.transitions[event], target_state)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateResetLogic(unittest.TestCase):
"""🔄 tests comprehensive לlogic of reset"""
    
    def setUp(self):
"""🔧 setup data"""
        self.mock_moves = Mock(spec=Moves)
        
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.reset = Mock()
        
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.reset = Mock()
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
    def test_reset_with_basic_command(self):
"""🧪 reset with command basic"""
        timestamp = 1500
        cmd = Command(timestamp, "test_piece", "move", [2, 3])
        
        self.state.reset(cmd)
        
# checking שהstate עודכן
        self.assertEqual(self.state.current_command, cmd)
        self.assertEqual(self.state.state_start_time, timestamp)
        
# checking שהcomponents קיבלו reset
        self.mock_graphics.reset.assert_called_once_with(cmd)
        self.mock_physics.reset.assert_called_once_with(cmd)
        
    def test_reset_with_different_timestamps(self):
"""🧪 reset with timestamps different"""
        timestamps = [0, 100, 1000, 5000, 999999]
        
        for timestamp in timestamps:
            with self.subTest(timestamp=timestamp):
                cmd = Command(timestamp, "piece", "action", [])
                self.state.reset(cmd)
                
                self.assertEqual(self.state.state_start_time, timestamp)
                
    def test_reset_sequence(self):
"""🧪 רצף of resets"""
        commands = [
            Command(1000, "piece1", "move", [1, 1]),
            Command(2000, "piece2", "jump", [2, 2]),
            Command(3000, "piece3", "attack", [3, 3]),
            Command(4000, "piece4", "defend", [4, 4])
        ]
        
        for cmd in commands:
            self.state.reset(cmd)
            
# checking שהcommand האחרון שמור
            self.assertEqual(self.state.current_command, cmd)
            self.assertEqual(self.state.state_start_time, cmd.timestamp)
            
# checking שreset נקרא number הפעמים הנכון
        self.assertEqual(self.mock_graphics.reset.call_count, 4)
        self.assertEqual(self.mock_physics.reset.call_count, 4)
        
    def test_reset_with_various_command_types(self):
"""🧪 reset with different command types"""
        command_types = [
            "move", "jump", "attack", "defend", "special",
            "long_move", "quick_action", "complex_maneuver"
        ]
        
        for cmd_type in command_types:
            with self.subTest(command_type=cmd_type):
                cmd = Command(1000, "test", cmd_type, [])
                self.state.reset(cmd)
                
                self.assertEqual(self.state.current_command.type, cmd_type)

if __name__ == '__main__':
print("🧪 running tests comprehensive for class State...")
    print("=" * 60)
    unittest.main(verbosity=2)
