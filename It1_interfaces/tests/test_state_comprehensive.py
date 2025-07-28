#!/usr/bin/env python3
"""
🧪 טסטים מקיפים ומעמיקים למחלקת State - כיסוי של 100%
בדיקת כל פונקציה, מצב וטרנזישן במערכת State
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
except ImportError as e:
    print(f"⚠️ Import error in test_state_comprehensive.py: {e}")
    HAS_IMPORTS = False

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestHelperFunctions(unittest.TestCase):
    """🔧 טסטים לפונקציות עזר של State module"""
    
    def test_extract_piece_type_from_sprites_path_string(self):
        """🧪 בדיקת חילוץ סוג כלי מנתיב string"""
        test_cases = [
            ("pieces/PW/states/idle/sprites", "PW"),
            ("pieces/BB/states/move/sprites", "BB"),
            ("pieces/KW/states/jump/sprites", "KW"),
            ("pieces/QB/states/long_rest/sprites", "QB"),
            ("pieces/NB/states/short_rest/sprites", "NB"),
        ]
        
        for path, expected in test_cases:
            with self.subTest(path=path):
                result = extract_piece_type_from_sprites_path(path)
                self.assertEqual(result, expected, f"Failed for path: {path}")
        
    def test_extract_piece_type_from_sprites_path_pathlib(self):
        """🧪 בדיקת חילוץ סוג כלי מנתיב pathlib.Path"""
        path = pathlib.Path("pieces/RW/states/move/sprites")
        result = extract_piece_type_from_sprites_path(path)
        self.assertEqual(result, "RW")
        
    def test_extract_piece_type_invalid_paths(self):
        """🧪 בדיקת נתיבים לא תקינים - צריכים להחזיר None"""
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
                result = extract_piece_type_from_sprites_path(path)
                self.assertIsNone(result, f"Path '{path}' should return None")
                
    def test_construct_sprites_path_for_state_valid_paths(self):
        """🧪 בדיקת בניית נתיב sprites לstate חדש"""
        test_cases = [
            ("pieces/PW/states/idle/sprites", "move", "pieces/PW/states/move/sprites"),
            ("pieces/BB/states/jump/sprites", "idle", "pieces/BB/states/idle/sprites"),
            ("pieces/KW/states/long_rest/sprites", "short_rest", "pieces/KW/states/short_rest/sprites"),
        ]
        
        for current_path, target_state, expected_str in test_cases:
            with self.subTest(current=current_path, target=target_state):
                result = construct_sprites_path_for_state(current_path, target_state)
                expected = pathlib.Path(expected_str)
                self.assertEqual(result, expected)
                
    def test_construct_sprites_path_for_state_invalid_fallback(self):
        """🧪 בדיקת fallback לנתיב לא תקין"""
        invalid_path = "invalid/structure"
        target_state = "move"
        result = construct_sprites_path_for_state(invalid_path, target_state)
        self.assertEqual(result, invalid_path)  # Should return original path as fallback

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateInitialization(unittest.TestCase):
    """🏗️ טסטים מקיפים לאתחול State"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
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
        
    def test_initialization_default_state(self):
        """🧪 אתחול עם state ברירת מחדל (idle)"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
        # בדיקת כל המאפיינים
        self.assertEqual(state.moves, self.mock_moves)
        self.assertEqual(state.graphics, self.mock_graphics)
        self.assertEqual(state.physics, self.mock_physics)
        self.assertEqual(state.state, "idle")  # Default
        self.assertEqual(state.transitions, {})
        self.assertEqual(state.state_start_time, 0)
        self.assertIsNone(state.current_command)
        self.assertFalse(state.is_rest_state)
        self.assertEqual(state.rest_duration_ms, 0)
        
    def test_initialization_custom_state(self):
        """🧪 אתחול עם state מותאם אישית"""
        custom_states = ["move", "jump", "long_rest", "short_rest", "custom_state"]
        
        for state_name in custom_states:
            with self.subTest(state_name=state_name):
                state = State(self.mock_moves, self.mock_graphics, self.mock_physics, state_name)
                self.assertEqual(state.state, state_name)
                self.assertEqual(state.moves, self.mock_moves)
                self.assertEqual(state.graphics, self.mock_graphics)
                self.assertEqual(state.physics, self.mock_physics)
                
    def test_initialization_state_properties(self):
        """🧪 בדיקת כל המאפיינים הפנימיים"""
        state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "test_state")
        
        # בדיקת types
        self.assertIsInstance(state.transitions, dict)
        self.assertIsInstance(state.state_start_time, int)
        self.assertIsInstance(state.is_rest_state, bool)
        self.assertIsInstance(state.rest_duration_ms, int)
        self.assertIsInstance(state.state, str)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateCopy(unittest.TestCase):
    """📋 טסטים מקיפים לfunctionality של copy"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.state_name = "idle"
        self.mock_graphics.copy.return_value = self.mock_graphics
        
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.copy.return_value = self.mock_physics
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "test_state")
        
    def test_copy_basic_properties(self):
        """🧪 בדיקת העתקת מאפיינים בסיסיים"""
        # הגדרת מאפיינים מיוחדים
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 1500
        
        copied_state = self.state.copy()
        
        # בדיקת שכל המאפיינים הועתקו נכון
        self.assertEqual(copied_state.state, self.state.state)
        self.assertEqual(copied_state.is_rest_state, self.state.is_rest_state)
        self.assertEqual(copied_state.rest_duration_ms, self.state.rest_duration_ms)
        self.assertEqual(copied_state.moves, self.state.moves)  # Same reference
        
    def test_copy_calls_component_copy(self):
        """🧪 בדיקת שhfunctions copy נקראות על הcomponents"""
        copied_state = self.state.copy()
        
        # בדיקת שneed_copy נקראו
        self.mock_graphics.copy.assert_called_once()
        self.mock_physics.copy.assert_called_once()
        
    def test_copy_resets_transitions(self):
        """🧪 בדיקת שhransitions מתאפסים במחלקה מועתקת"""
        # הוספת transitions למקור
        target_state = Mock()
        self.state.set_transition("test", target_state)
        
        copied_state = self.state.copy()
        
        # Transitions צריכים להיות ריקים בהעתק
        self.assertEqual(copied_state.transitions, {})
        
    def test_copy_graphics_state_name_fix(self):
        """🧪 בדיקת שstate_name מתקן בgraphics המועתק"""
        copied_state = self.state.copy()
        
        # בדיקת שstate_name הוגדר נכון
        self.assertEqual(copied_state.graphics.state_name, self.state.state)
        
    def test_copy_multiple_times(self):
        """🧪 בדיקת העתקות מרובות"""
        copy1 = self.state.copy()
        copy2 = self.state.copy()
        copy3 = copy1.copy()
        
        # כל העתק צריך להיות עצמאי
        self.assertNotEqual(copy1, copy2)
        self.assertNotEqual(copy1, copy3)
        self.assertNotEqual(copy2, copy3)
        
        # אבל עם אותם מאפיינים
        for copy_state in [copy1, copy2, copy3]:
            self.assertEqual(copy_state.state, self.state.state)
            self.assertEqual(copy_state.is_rest_state, self.state.is_rest_state)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateTransitions(unittest.TestCase):
    """🔄 טסטים מקיפים לטrנzitionים בין states"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_physics = Mock(spec=Physics)
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
    def test_set_single_transition(self):
        """🧪 הוספת transition יחיד"""
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        
        self.state.set_transition("command", target_state)
        
        self.assertEqual(self.state.transitions["command"], target_state)
        self.assertEqual(len(self.state.transitions), 1)
        
    def test_set_multiple_transitions(self):
        """🧪 הוספת transitions מרובים"""
        move_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        jump_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "jump")
        rest_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "rest")
        
        transitions = {
            "move": move_state,
            "jump": jump_state,
            "rest": rest_state,
            "complete": move_state,
            "timeout": jump_state
        }
        
        for event, target in transitions.items():
            self.state.set_transition(event, target)
            
        # בדיקת שכל הhransitions נוספו
        self.assertEqual(len(self.state.transitions), 5)
        for event, target in transitions.items():
            self.assertEqual(self.state.transitions[event], target)
            
    def test_overwrite_transition(self):
        """🧪 דריסת transition קיים"""
        state1 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "state1")
        state2 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "state2")
        
        # הוספה ראשונה
        self.state.set_transition("event", state1)
        self.assertEqual(self.state.transitions["event"], state1)
        
        # דריסה
        self.state.set_transition("event", state2)
        self.assertEqual(self.state.transitions["event"], state2)
        self.assertEqual(len(self.state.transitions), 1)
        
    def test_transition_with_special_characters(self):
        """🧪 transitions עם תווים מיוחדים"""
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "target")
        
        special_events = ["move-action", "jump_high", "rest.long", "complete!", "timeout?"]
        
        for event in special_events:
            with self.subTest(event=event):
                self.state.set_transition(event, target_state)
                self.assertEqual(self.state.transitions[event], target_state)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateReset(unittest.TestCase):
    """🔄 טסטים מקיפים לfunctionality של reset"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.reset = Mock()
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.reset = Mock()
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
    def test_reset_with_valid_command(self):
        """🧪 reset עם פקודה תקינה"""
        timestamp = int(time.time() * 1000)
        cmd = Command(timestamp, "test_piece", "move", [1, 1])
        
        self.state.reset(cmd)
        
        # בדיקת שהstate עודכן
        self.assertEqual(self.state.current_command, cmd)
        self.assertEqual(self.state.state_start_time, timestamp)
        
        # בדיקת שהcomponents עודכנו
        self.mock_graphics.reset.assert_called_once_with(cmd)
        self.mock_physics.reset.assert_called_once_with(cmd)
        
    def test_reset_multiple_times(self):
        """🧪 מספר resets ברצף"""
        timestamps = [1000, 2000, 3000]
        commands = [
            Command(timestamps[0], "piece1", "move", [1, 1]),
            Command(timestamps[1], "piece2", "jump", [2, 2]),
            Command(timestamps[2], "piece3", "rest", [])
        ]
        
        for i, cmd in enumerate(commands):
            with self.subTest(command=i):
                self.state.reset(cmd)
                
                self.assertEqual(self.state.current_command, cmd)
                self.assertEqual(self.state.state_start_time, timestamps[i])
                
        # בדיקת שreset נקרא מספר פעמים
        self.assertEqual(self.mock_graphics.reset.call_count, 3)
        self.assertEqual(self.mock_physics.reset.call_count, 3)
        
    def test_reset_with_different_command_types(self):
        """🧪 reset עם סוגי פקודות שונים"""
        command_types = ["move", "jump", "attack", "defend", "special"]
        
        for cmd_type in command_types:
            with self.subTest(command_type=cmd_type):
                cmd = Command(1000, "test", cmd_type, [])
                self.state.reset(cmd)
                
                self.assertEqual(self.state.current_command.type, cmd_type)

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateCanTransition(unittest.TestCase):
    """⏰ טסטים מקיפים לlogic של can_transition"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_physics = Mock(spec=Physics)
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
    def test_non_rest_state_always_can_transition(self):
        """🧪 state לא-מנוחה תמיד יכול לעבור transition"""
        self.state.is_rest_state = False
        
        test_times = [0, 100, 1000, 5000, 10000]
        
        for now_ms in test_times:
            with self.subTest(time=now_ms):
                self.assertTrue(self.state.can_transition(now_ms))
                
    def test_rest_state_before_duration(self):
        """🧪 state מנוחה לפני השלמת הזמן"""
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 2000
        self.state.state_start_time = 1000
        
        # זמנים לפני השלמת המנוחה
        early_times = [1000, 1500, 2500, 2999]
        
        for now_ms in early_times:
            with self.subTest(time=now_ms):
                self.assertFalse(self.state.can_transition(now_ms))
                
    def test_rest_state_after_duration(self):
        """🧪 state מנוחה אחרי השלמת הזמן"""
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 2000
        self.state.state_start_time = 1000
        
        # זמנים אחרי השלמת המנוחה (1000 + 2000 = 3000)
        late_times = [3000, 3001, 4000, 5000]
        
        for now_ms in late_times:
            with self.subTest(time=now_ms):
                self.assertTrue(self.state.can_transition(now_ms))
                
    def test_rest_state_edge_cases(self):
        """🧪 מקרי קצה לstate מנוחה"""
        self.state.is_rest_state = True
        
        # מקרה 1: אורך מנוחה 0
        self.state.rest_duration_ms = 0
        self.state.state_start_time = 1000
        self.assertTrue(self.state.can_transition(1000))
        
        # מקרה 2: זמן התחלה גבוה מהזמן הנוכחי (שגיאת timing)
        self.state.rest_duration_ms = 1000
        self.state.state_start_time = 2000
        self.assertFalse(self.state.can_transition(1500))
        
    def test_rest_state_various_durations(self):
        """🧪 state מנוחה עם משכי זמן שונים"""
        durations = [100, 500, 1000, 2000, 5000]
        start_time = 1000
        
        for duration in durations:
            with self.subTest(duration=duration):
                self.state.is_rest_state = True
                self.state.rest_duration_ms = duration
                self.state.state_start_time = start_time
                
                # לפני סיום
                self.assertFalse(self.state.can_transition(start_time + duration - 1))
                # בסיום בדיוק
                self.assertTrue(self.state.can_transition(start_time + duration))
                # אחרי סיום
                self.assertTrue(self.state.can_transition(start_time + duration + 100))

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestCreateTransitionState(unittest.TestCase):
    """🎭 טסטים מקיפים ליצירת transition states"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        
        # Mock graphics עם כל המאפיינים הנדרשים
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.sprites_folder = "pieces/PW/states/idle/sprites"
        self.mock_graphics.cell_size = 64
        self.mock_graphics.state_name = "idle"
        self.mock_graphics.copy.return_value = self.mock_graphics
        
        # Mock physics עם מאפיינים נדרשים
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.current_cell = (0, 0)
        self.mock_physics.target_cell = (1, 1)
        self.mock_physics.copy.return_value = self.mock_physics
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_create_transition_state_basic(self, mock_graphics_factory):
        """🧪 יצירת transition state בסיסי"""
        # הגדרת template state
        template_graphics = Mock()
        template_graphics.sprites_folder = "pieces/PW/states/move/sprites"
        template_graphics.cell_size = 64
        template_physics = Mock()
        
        template_state = State(self.mock_moves, template_graphics, template_physics, "move")
        template_state.is_rest_state = True
        template_state.rest_duration_ms = 1000
        
        # הגדרת mock factory
        new_graphics = Mock()
        mock_graphics_factory.create.return_value = new_graphics
        
        # יצירת command
        cmd = Command(1000, "test", "move", [])
        
        # יצירת transition state
        new_state = self.state._create_transition_state(template_state, cmd)
        
        # בדיקת המאפיינים החדשים
        self.assertEqual(new_state.state, "move")
        self.assertEqual(new_state.is_rest_state, True)
        self.assertEqual(new_state.rest_duration_ms, 1000)
        
        # בדיקת שGraphicsFactory נקרא
        mock_graphics_factory.create.assert_called_once()
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_create_transition_state_with_transitions(self, mock_graphics_factory):
        """🧪 יצירת transition state עם transitions"""
        # יצירת template עם transitions
        template_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        idle_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        template_state.transitions = {"complete": idle_state, "timeout": idle_state}
        
        mock_graphics_factory.create.return_value = Mock()
        cmd = Command(1000, "test", "move", [])
        
        new_state = self.state._create_transition_state(template_state, cmd)
        
        # בדיקת שhransitions הועתקו
        self.assertEqual(new_state.transitions, template_state.transitions)
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_create_transition_state_physics_copy(self, mock_graphics_factory):
        """🧪 בדיקת העתקת מצב physics"""
        # הגדרת מצב physics נוכחי
        self.state.physics.current_cell = (2, 3)
        self.state.physics.target_cell = (4, 5)
        
        template_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "jump")
        mock_graphics_factory.create.return_value = Mock()
        cmd = Command(1000, "test", "jump", [])
        
        new_state = self.state._create_transition_state(template_state, cmd)
        
        # בדיקת שמצב physics הועתק
        self.assertEqual(new_state.physics.current_cell, (2, 3))
        self.assertEqual(new_state.physics.target_cell, (4, 5))
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_create_transition_state_graphics_path_construction(self, mock_graphics_factory):
        """🧪 בדיקת בניית נתיב sprites נכון"""
        template_graphics = Mock()
        template_graphics.sprites_folder = "pieces/BB/states/jump/sprites"
        template_graphics.cell_size = 32
        
        template_state = State(self.mock_moves, template_graphics, self.mock_physics, "jump")
        
        mock_graphics_factory.create.return_value = Mock()
        cmd = Command(1000, "test", "jump", [])
        
        self.state._create_transition_state(template_state, cmd)
        
        # בדיקת הarguments שנשלחו לfactory
        call_args = mock_graphics_factory.create.call_args
        self.assertIsNotNone(call_args)
        
        # בדיקת שstate name נשלח נכון
        self.assertEqual(call_args[0][3], "jump")  # state name argument

if __name__ == '__main__':
    # הרצת כל הטסטים עם reporting מפורט
    unittest.main(verbosity=2)
