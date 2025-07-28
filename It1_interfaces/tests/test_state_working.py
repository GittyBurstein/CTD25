#!/usr/bin/env python3
"""
🧪 טסטים מקיפים למחלקת State - גרסה מתוקנת
בדיקת כל פונקציה, מצב וטרנזישן במערכת State עם כיסוי של 100%
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import pathlib
import time

# Add parent directory to path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
# נסה לייבא the הmodules
    import State
    import Command
    import Moves
    import Graphics  
    import Physics
    HAS_IMPORTS = True
print("✅ all הimports הצליחו!")
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    HAS_IMPORTS = False

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateHelperFunctions(unittest.TestCase):
"""🔧 tests לפונקציות עזר of State module"""
    
    def test_extract_piece_type_from_sprites_path_string(self):
"""🧪 checking חילוץ סוג piece מנתיב string"""
        test_cases = [
            ("pieces/PW/states/idle/sprites", "PW"),
            ("pieces/BB/states/move/sprites", "BB"),
            ("pieces/KW/states/jump/sprites", "KW"),
            ("pieces/QB/states/long_rest/sprites", "QB"),
            ("pieces/NB/states/short_rest/sprites", "NB"),
        ]
        
        for path, expected in test_cases:
            with self.subTest(path=path):
                result = State.extract_piece_type_from_sprites_path(path)
                self.assertEqual(result, expected, f"Failed for path: {path}")
        
    def test_extract_piece_type_from_sprites_path_pathlib(self):
"""🧪 checking חילוץ סוג piece מנתיב pathlib.Path"""
        path = pathlib.Path("pieces/RW/states/move/sprites")
        result = State.extract_piece_type_from_sprites_path(path)
        self.assertEqual(result, "RW")
        
    def test_extract_piece_type_invalid_paths(self):
"""🧪 checking paths no תקינים - צריכים להחזיר None"""
        invalid_paths = [
            "invalid/path",
            "pieces/PW",
            "pieces/PW/states",
            "not/correct/structure/at/all",
            "pieces/states/idle/sprites",  # Missing piece type
            "pieces/PW/wrong/idle/sprites",  # Wrong structure
            "",  # Empty string
            "sprites",  # Just sprites
        ]
        
        for path in invalid_paths:
            with self.subTest(path=path):
                result = State.extract_piece_type_from_sprites_path(path)
                self.assertIsNone(result, f"Path '{path}' should return None")
                
    def test_construct_sprites_path_for_state_valid_paths(self):
"""🧪 checking בניית path sprites לstate new"""
        test_cases = [
            ("pieces/PW/states/idle/sprites", "move", "pieces/PW/states/move/sprites"),
            ("pieces/BB/states/jump/sprites", "idle", "pieces/BB/states/idle/sprites"),
            ("pieces/KW/states/long_rest/sprites", "short_rest", "pieces/KW/states/short_rest/sprites"),
        ]
        
        for current_path, target_state, expected_str in test_cases:
            with self.subTest(current=current_path, target=target_state):
                result = State.construct_sprites_path_for_state(current_path, target_state)
                expected = pathlib.Path(expected_str)
                self.assertEqual(result, expected)
                
    def test_construct_sprites_path_for_state_invalid_fallback(self):
"""🧪 checking fallback לנתיב no valid"""
        invalid_path = "invalid/structure"
        target_state = "move"
        result = State.construct_sprites_path_for_state(invalid_path, target_state)
        self.assertEqual(result, invalid_path)  # Should return original path as fallback

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateBasics(unittest.TestCase):
"""🏗️ tests basic for class State"""
    
    def setUp(self):
"""🔧 setup data for each test"""
        self.mock_moves = Mock(spec=Moves.Moves if hasattr(Moves, 'Moves') else object)
        
        self.mock_graphics = Mock(spec=Graphics.Graphics if hasattr(Graphics, 'Graphics') else object)
        self.mock_graphics.sprites_folder = "pieces/PW/states/idle/sprites"
        self.mock_graphics.cell_size = 64
        self.mock_graphics.state_name = "idle"
        self.mock_graphics.copy.return_value = self.mock_graphics
        self.mock_graphics.reset = Mock()
        self.mock_graphics.update = Mock()
        
        self.mock_physics = Mock(spec=Physics.Physics if hasattr(Physics, 'Physics') else object)
        self.mock_physics.current_cell = (0, 0)
        self.mock_physics.target_cell = (1, 1)
        self.mock_physics.is_moving = False
        self.mock_physics.copy.return_value = self.mock_physics
        self.mock_physics.reset = Mock()
        self.mock_physics.update = Mock(return_value=False)
        
    def test_state_initialization_default(self):
"""🧪 initialization state with ברירת מחדל"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
        self.assertEqual(state.moves, self.mock_moves)
        self.assertEqual(state.graphics, self.mock_graphics)
        self.assertEqual(state.physics, self.mock_physics)
        self.assertEqual(state.state, "idle")  # Default state name
        self.assertEqual(state.transitions, {})
        self.assertEqual(state.state_start_time, 0)
        self.assertIsNone(state.current_command)
        self.assertFalse(state.is_rest_state)
        self.assertEqual(state.rest_duration_ms, 0)
        
    def test_state_initialization_custom(self):
"""🧪 initialization state with שם מותאם אישית"""
        custom_states = ["move", "jump", "long_rest", "short_rest", "custom_state"]
        
        for state_name in custom_states:
            with self.subTest(state_name=state_name):
                state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, state_name)
                self.assertEqual(state.state, state_name)
                self.assertEqual(state.moves, self.mock_moves)
                self.assertEqual(state.graphics, self.mock_graphics)
                self.assertEqual(state.physics, self.mock_physics)
                
    def test_state_copy(self):
"""🧪 checking copying state"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "test_state")
        
# הגדרת מאפיינים מיוחדים
        state.is_rest_state = True
        state.rest_duration_ms = 1500
        
        copied_state = state.copy()
        
# checking שכל המאפיינים הועתקו נכון
        self.assertEqual(copied_state.state, state.state)
        self.assertEqual(copied_state.is_rest_state, state.is_rest_state)
        self.assertEqual(copied_state.rest_duration_ms, state.rest_duration_ms)
        self.assertEqual(copied_state.moves, state.moves)  # Same reference
        
# checking שcopy נקראו על הcomponents
        self.mock_graphics.copy.assert_called()
        self.mock_physics.copy.assert_called()
        
# checking שtransitions מתאפסים במחלקה מועתקת
        self.assertEqual(copied_state.transitions, {})
        
    def test_set_transitions(self):
"""🧪 הגדרת transitions בין states"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
# creating target states
        move_state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        jump_state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "jump")
        
# הגדרת transitions
        state.set_transition("move", move_state)
        state.set_transition("jump", jump_state)
        
# checking שהtransitions נוספו
        self.assertEqual(len(state.transitions), 2)
        self.assertEqual(state.transitions["move"], move_state)
        self.assertEqual(state.transitions["jump"], jump_state)
        
    def test_reset_state(self):
"""🧪 checking reset of state"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
        timestamp = int(time.time() * 1000)
        cmd = Command.Command(timestamp, "test_piece", "move", [1, 1])
        
        state.reset(cmd)
        
# checking שהstate עודכן
        self.assertEqual(state.current_command, cmd)
        self.assertEqual(state.state_start_time, timestamp)
        
# checking שהcomponents עודכנו
        self.mock_graphics.reset.assert_called_once_with(cmd)
        self.mock_physics.reset.assert_called_once_with(cmd)
        
    def test_can_transition_logic(self):
"""🧪 checking לוגיקת can_transition"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
# Non-rest state - תמיד יכול לעבור transition
        state.is_rest_state = False
        self.assertTrue(state.can_transition(0))
        self.assertTrue(state.can_transition(1000))
        self.assertTrue(state.can_transition(5000))
        
# Rest state - תלוי בזמן
        state.is_rest_state = True
        state.rest_duration_ms = 2000
        state.state_start_time = 1000
        
# לפני השלמת הזמן
        self.assertFalse(state.can_transition(1500))  # 1500 < 1000 + 2000
        
# אחרי השלמת הזמן
        self.assertTrue(state.can_transition(3500))   # 3500 >= 1000 + 2000
        
    def test_get_command(self):
"""🧪 checking get_command"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
# בתחילה no command
        self.assertIsNone(state.get_command())
        
# אחרי reset with command
        cmd = Command.Command(1000, "test_piece", "move", [1, 1])
        state.reset(cmd)
        
        result = state.get_command()
        self.assertEqual(result, cmd)
        
    def test_update_basic(self):
"""🧪 checking update basic"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
        now_ms = 1000
        
        # Mock returns False for movement complete
        self.mock_physics.update.return_value = False
        
        result = state.update(now_ms)
        
# checking שהcomponents עודכנו
        self.mock_graphics.update.assert_called_once_with(now_ms)
        self.mock_physics.update.assert_called_once_with(now_ms)
        
# צריך להחזיר the עצמו (no transitions)
        self.assertEqual(result, state)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateFactoryFunctions(unittest.TestCase):
"""🏭 tests לפונקציות factory of states"""
    
    def setUp(self):
"""🔧 setup data for each test"""
        self.mock_moves = Mock()
        self.mock_graphics = Mock()
        self.mock_physics = Mock()
        self.idle_state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
    def test_create_long_rest_state(self):
"""🧪 creating long rest state"""
        rest_state = State.create_long_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
# checking מאפיינים
        self.assertEqual(rest_state.state, "long_rest")
        self.assertTrue(rest_state.is_rest_state)
        self.assertEqual(rest_state.rest_duration_ms, 2000)  # 2 seconds
        
# checking timeout transition
        self.assertEqual(rest_state.transitions["timeout"], self.idle_state)
        
    def test_create_short_rest_state(self):
"""🧪 creating short rest state"""
        rest_state = State.create_short_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
# checking מאפיינים
        self.assertEqual(rest_state.state, "short_rest")
        self.assertTrue(rest_state.is_rest_state)
        self.assertEqual(rest_state.rest_duration_ms, 1000)  # 1 second
        
# checking timeout transition
        self.assertEqual(rest_state.transitions["timeout"], self.idle_state)
        
    def test_rest_states_durations_comparison(self):
"""🧪 השוואת משכי זמן בין rest states"""
        short_rest = State.create_short_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        long_rest = State.create_long_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
# long rest צריך להיות more ארוך מ-short rest
        self.assertGreater(long_rest.rest_duration_ms, short_rest.rest_duration_ms)
        self.assertEqual(long_rest.rest_duration_ms, 2 * short_rest.rest_duration_ms)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateAdvancedScenarios(unittest.TestCase):
"""🎯 tests למקרי שימוש advanced"""
    
    def setUp(self):
"""🔧 setup data for each test"""
        self.mock_moves = Mock()
        self.mock_graphics = Mock()
        self.mock_graphics.copy.return_value = self.mock_graphics
        self.mock_graphics.update = Mock()
        self.mock_graphics.reset = Mock()
        
        self.mock_physics = Mock()
        self.mock_physics.copy.return_value = self.mock_physics
        self.mock_physics.update = Mock(return_value=False)
        self.mock_physics.reset = Mock()
        self.mock_physics.is_moving = False
        
    def test_multiple_transitions_chain(self):
"""🧪 שרשרת of transitions מרובים"""
# creating שרשרת: idle -> move -> rest -> idle
        idle_state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        move_state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        rest_state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics, "rest")
        
# הגדרת transitions
        idle_state.set_transition("move", move_state)
        move_state.set_transition("complete", rest_state)
        rest_state.set_transition("timeout", idle_state)
        
# checking שכל הtransitions הוגדרו נכון
        self.assertEqual(idle_state.transitions["move"], move_state)
        self.assertEqual(move_state.transitions["complete"], rest_state)
        self.assertEqual(rest_state.transitions["timeout"], idle_state)
        
    def test_command_types_handling(self):
"""🧪 טיפול בdifferent command types"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
        command_types = ["move", "jump", "attack", "defend", "special_ability"]
        
        for cmd_type in command_types:
            with self.subTest(command_type=cmd_type):
                cmd = Command.Command(1000, "test", cmd_type, [])
                state.reset(cmd)
                
                retrieved_cmd = state.get_command()
                self.assertEqual(retrieved_cmd.type, cmd_type)
                
    def test_timing_precision(self):
"""🧪 checking דיוק במדידת זמנים"""
        state = State.State(self.mock_moves, self.mock_graphics, self.mock_physics)
        state.is_rest_state = True
        state.rest_duration_ms = 1000
        state.state_start_time = 5000
        
# cases of קצה of timing
        test_cases = [
            (5999, False),  # 1ms לפני סיום
            (6000, True),   # בדיוק בזמן סיום
            (6001, True),   # 1ms אחרי סיום
        ]
        
        for test_time, expected in test_cases:
            with self.subTest(time=test_time):
                result = state.can_transition(test_time)
                self.assertEqual(result, expected)

if __name__ == '__main__':
print("🧪 running tests comprehensive for class State...")
    print("=" * 60)
    unittest.main(verbosity=2)
