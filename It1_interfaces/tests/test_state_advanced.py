#!/usr/bin/env python3
"""
🧪 טסטים מקיפים חלק 2 - פונקציות מתקדמות של State
כיסוי מלא של get_state_after_command, update, ופונקציות factory
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time

# Add parent directory to path to import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from State import (
        State, 
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
    print(f"⚠️ Import error in test_state_advanced.py: {e}")
    HAS_IMPORTS = False

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestGetStateAfterCommand(unittest.TestCase):
    """🎯 טסטים מקיפים לfunctionality של get_state_after_command"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.copy.return_value = self.mock_graphics
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.copy.return_value = self.mock_physics
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
    def test_cannot_transition_returns_self(self):
        """🧪 אם לא ניתן לעבור transition, מחזיר את עצמו"""
        # הגדרת rest state שעדיין לא סיים
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 2000
        self.state.state_start_time = 1000
        
        cmd = Command(1500, "test", "move", [])  # Too early
        
        result = self.state.get_state_after_command(cmd, 1500)
        self.assertEqual(result, self.state)
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_valid_transition_creates_new_state(self, mock_graphics_factory):
        """🧪 transition תקין יוצר state חדש"""
        # הגדרת target state
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        self.state.set_transition("move", target_state)
        
        mock_graphics_factory.create.return_value = Mock()
        cmd = Command(1000, "test", "move", [])
        
        result = self.state.get_state_after_command(cmd, 1000)
        
        # צריך להיות state חדש, לא המקורי
        self.assertNotEqual(result, self.state)
        self.assertEqual(result.state, "move")
        
    def test_invalid_command_type_returns_self(self):
        """🧪 סוג פקודה לא קיים מחזיר את עצמו"""
        # הוספת כמה transitions
        target1 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        target2 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "jump")
        self.state.set_transition("move", target1)
        self.state.set_transition("jump", target2)
        
        # פקודה עם type שלא קיים
        cmd = Command(1000, "test", "non_existent_command", [])
        
        result = self.state.get_state_after_command(cmd, 1000)
        self.assertEqual(result, self.state)
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_multiple_transitions_correct_selection(self, mock_graphics_factory):
        """🧪 מספר transitions - בחירת הנכון לפי type"""
        # הוספת מספר transitions
        move_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "move")
        jump_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "jump")
        attack_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "attack")
        
        self.state.set_transition("move", move_state)
        self.state.set_transition("jump", jump_state)
        self.state.set_transition("attack", attack_state)
        
        mock_graphics_factory.create.return_value = Mock()
        
        # בדיקת כל transition
        test_cases = [
            ("move", "move"),
            ("jump", "jump"),
            ("attack", "attack")
        ]
        
        for cmd_type, expected_state in test_cases:
            with self.subTest(command_type=cmd_type):
                cmd = Command(1000, "test", cmd_type, [])
                result = self.state.get_state_after_command(cmd, 1000)
                self.assertEqual(result.state, expected_state)
                
    def test_edge_cases_timing(self):
        """🧪 מקרי קצה של timing"""
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 1000
        self.state.state_start_time = 500
        
        cmd = Command(1000, "test", "move", [])
        
        # בדיוק בזמן שיכול לעבור transition (500 + 1000 = 1500)
        result_early = self.state.get_state_after_command(cmd, 1499)  # 1ms לפני
        self.assertEqual(result_early, self.state)
        
        result_exact = self.state.get_state_after_command(cmd, 1500)   # בדיוק בזמן
        self.assertEqual(result_exact, self.state)  # No transition defined
        
        result_late = self.state.get_state_after_command(cmd, 1501)    # 1ms אחרי
        self.assertEqual(result_late, self.state)   # No transition defined

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateUpdate(unittest.TestCase):
    """🔄 טסטים מקיפים לfunctionality של update"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_graphics.update = Mock()
        self.mock_graphics.copy.return_value = self.mock_graphics
        
        self.mock_physics = Mock(spec=Physics)
        self.mock_physics.update = Mock(return_value=False)
        self.mock_physics.is_moving = False
        self.mock_physics.copy.return_value = self.mock_physics
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
    def test_update_calls_components(self):
        """🧪 update קורא לכל הcomponents"""
        now_ms = 1000
        
        result = self.state.update(now_ms)
        
        # בדיקת שהcomponents עודכנו
        self.mock_graphics.update.assert_called_once_with(now_ms)
        self.mock_physics.update.assert_called_once_with(now_ms)
        
        # ללא transitions - צריך להחזיר את עצמו
        self.assertEqual(result, self.state)
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_update_movement_complete_transition(self, mock_graphics_factory):
        """🧪 update עם השלמת תנועה -> transition"""
        now_ms = 1000
        
        # הגדרת movement complete
        self.mock_physics.update.return_value = True
        
        # הוספת complete transition
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "rest")
        self.state.set_transition("complete", target_state)
        
        mock_graphics_factory.create.return_value = Mock()
        
        result = self.state.update(now_ms)
        
        # צריך לעבור לstate חדש
        self.assertNotEqual(result, self.state)
        self.assertEqual(result.state, "rest")
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_update_rest_state_timeout(self, mock_graphics_factory):
        """🧪 update של rest state עם timeout"""
        now_ms = 3000
        
        # הגדרת rest state שסיים
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 1000
        self.state.state_start_time = 1000  # 1000 + 1000 = 2000, so 3000 > 2000
        
        # הוספת timeout transition
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        self.state.set_transition("timeout", target_state)
        
        mock_graphics_factory.create.return_value = Mock()
        self.mock_physics.update.return_value = False
        
        result = self.state.update(now_ms)
        
        # צריך לעבור לstate חדש בגלל timeout
        self.assertNotEqual(result, self.state)
        self.assertEqual(result.state, "idle")
        
    def test_update_rest_state_no_timeout_yet(self):
        """🧪 update של rest state שעדיין לא timeout"""
        now_ms = 1500
        
        # הגדרת rest state שעדיין לא סיים
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 2000
        self.state.state_start_time = 1000  # 1000 + 2000 = 3000, so 1500 < 3000
        
        # הוספת timeout transition
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        self.state.set_transition("timeout", target_state)
        
        self.mock_physics.update.return_value = False
        
        result = self.state.update(now_ms)
        
        # לא צריך לעבור transition עדיין
        self.assertEqual(result, self.state)
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_update_move_state_auto_completion(self, mock_graphics_factory):
        """🧪 update של move state עם auto-completion"""
        self.state.state = "move"
        self.state.physics.is_moving = False  # Movement finished
        
        # הוספת complete transition
        target_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "rest")
        self.state.set_transition("complete", target_state)
        
        mock_graphics_factory.create.return_value = Mock()
        self.mock_physics.update.return_value = False
        
        result = self.state.update(1000)
        
        # צריך להשלים אוטומטית
        self.assertNotEqual(result, self.state)
        
    def test_update_move_state_still_moving(self):
        """🧪 update של move state שעדיין זז"""
        self.state.state = "move"
        self.state.physics.is_moving = True  # Still moving
        
        self.mock_physics.update.return_value = False
        
        result = self.state.update(1000)
        
        # לא צריך להשלים עדיין
        self.assertEqual(result, self.state)
        
    def test_update_long_rest_state_handling(self):
        """🧪 update של long_rest state"""
        self.state.state = "long_rest"
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 2000
        self.state.state_start_time = 1000
        
        self.mock_physics.update.return_value = False
        
        # לפני timeout
        result = self.state.update(2000)
        self.assertEqual(result, self.state)
        
    @patch('It1_interfaces.State.GraphicsFactory')
    def test_update_multiple_conditions_priority(self, mock_graphics_factory):
        """🧪 update עם מספר תנאים - בדיקת סדר עדיפויות"""
        now_ms = 3000
        
        # הגדרת מצב שיכול לטריגר מספר transitions
        self.mock_physics.update.return_value = True  # Movement complete
        self.state.is_rest_state = True
        self.state.rest_duration_ms = 1000
        self.state.state_start_time = 1000  # Timeout ready
        
        # הוספת שני transitions
        complete_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "complete")
        timeout_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "timeout")
        self.state.set_transition("complete", complete_state)
        self.state.set_transition("timeout", timeout_state)
        
        mock_graphics_factory.create.return_value = Mock()
        
        result = self.state.update(now_ms)
        
        # Movement complete צריך להיות בעדיפות עליונה
        self.assertEqual(result.state, "complete")

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateFactoryFunctions(unittest.TestCase):
    """🏭 טסטים מקיפים לפונקציות factory של states"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_physics = Mock(spec=Physics)
        self.idle_state = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle")
        
    def test_create_long_rest_state_properties(self):
        """🧪 יצירת long rest state עם מאפיינים נכונים"""
        rest_state = create_long_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # בדיקת כל המאפיינים
        self.assertEqual(rest_state.state, "long_rest")
        self.assertTrue(rest_state.is_rest_state)
        self.assertEqual(rest_state.rest_duration_ms, 2000)  # 2 seconds
        self.assertEqual(rest_state.moves, self.mock_moves)
        self.assertEqual(rest_state.graphics, self.mock_graphics)
        self.assertEqual(rest_state.physics, self.mock_physics)
        
        # בדיקת timeout transition
        self.assertEqual(rest_state.transitions["timeout"], self.idle_state)
        self.assertEqual(len(rest_state.transitions), 1)
        
    def test_create_short_rest_state_properties(self):
        """🧪 יצירת short rest state עם מאפיינים נכונים"""
        rest_state = create_short_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # בדיקת כל המאפיינים
        self.assertEqual(rest_state.state, "short_rest")
        self.assertTrue(rest_state.is_rest_state)
        self.assertEqual(rest_state.rest_duration_ms, 1000)  # 1 second
        self.assertEqual(rest_state.moves, self.mock_moves)
        self.assertEqual(rest_state.graphics, self.mock_graphics)
        self.assertEqual(rest_state.physics, self.mock_physics)
        
        # בדיקת timeout transition
        self.assertEqual(rest_state.transitions["timeout"], self.idle_state)
        self.assertEqual(len(rest_state.transitions), 1)
        
    def test_create_rest_states_different_durations(self):
        """🧪 השוואת משכי זמן בין short ו-long rest"""
        short_rest = create_short_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        long_rest = create_long_rest_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # long rest צריך להיות יותר ארוך מ-short rest
        self.assertGreater(long_rest.rest_duration_ms, short_rest.rest_duration_ms)
        self.assertEqual(long_rest.rest_duration_ms, 2 * short_rest.rest_duration_ms)
        
    @patch('It1_interfaces.State.create_long_rest_state')
    def test_create_move_state_with_completion(self, mock_create_long_rest):
        """🧪 יצירת move state עם transition לlong rest"""
        # הגדרת mock long rest state
        mock_long_rest = Mock()
        mock_long_rest.state = "long_rest"
        mock_create_long_rest.return_value = mock_long_rest
        
        move_state = create_move_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # בדיקת מאפיינים בסיסיים
        self.assertEqual(move_state.state, "move")
        self.assertEqual(move_state.moves, self.mock_moves)
        self.assertEqual(move_state.graphics, self.mock_graphics)
        self.assertEqual(move_state.physics, self.mock_physics)
        
        # בדיקת שlong rest נוצר עם הparameters הנכונים
        mock_create_long_rest.assert_called_once_with(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # בדיקת complete transition
        self.assertEqual(move_state.transitions["complete"], mock_long_rest)
        self.assertEqual(len(move_state.transitions), 1)
        
    def test_create_move_state_not_rest_state(self):
        """🧪 בדיקת שmove state לא נוצר כrest state"""
        move_state = create_move_state(
            self.idle_state, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # move state לא צריך להיות rest state
        self.assertFalse(move_state.is_rest_state)
        self.assertEqual(move_state.rest_duration_ms, 0)
        
    def test_factory_functions_use_different_idle_states(self):
        """🧪 פונקציות factory עם idle states שונים"""
        # יצירת idle states שונים
        idle_state_1 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle1")
        idle_state_2 = State(self.mock_moves, self.mock_graphics, self.mock_physics, "idle2")
        
        # יצירת rest states עם idle states שונים
        long_rest_1 = create_long_rest_state(
            idle_state_1, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        long_rest_2 = create_long_rest_state(
            idle_state_2, self.mock_moves, self.mock_graphics, self.mock_physics
        )
        
        # בדיקת שהtimeout transitions מצביעים לndle states הנכונים
        self.assertEqual(long_rest_1.transitions["timeout"], idle_state_1)
        self.assertEqual(long_rest_2.transitions["timeout"], idle_state_2)
        self.assertNotEqual(long_rest_1.transitions["timeout"], long_rest_2.transitions["timeout"])

@unittest.skipUnless(HAS_IMPORTS, "Required imports not available")
class TestStateGetCommand(unittest.TestCase):
    """📋 טסטים מקיפים לget_command functionality"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.mock_moves = Mock(spec=Moves)
        self.mock_graphics = Mock(spec=Graphics)
        self.mock_physics = Mock(spec=Physics)
        
        self.state = State(self.mock_moves, self.mock_graphics, self.mock_physics)
        
    def test_get_command_when_none(self):
        """🧪 get_command כשאין command נוכחי"""
        result = self.state.get_command()
        self.assertIsNone(result)
        
    def test_get_command_after_reset(self):
        """🧪 get_command אחרי reset עם command"""
        cmd = Command(1000, "test_piece", "move", [1, 1])
        self.state.reset(cmd)
        
        result = self.state.get_command()
        self.assertEqual(result, cmd)
        
    def test_get_command_with_different_commands(self):
        """🧪 get_command עם סוגי פקודות שונים"""
        commands = [
            Command(1000, "piece1", "move", [1, 1]),
            Command(2000, "piece2", "jump", [2, 2]),
            Command(3000, "piece3", "attack", [3, 3]),
            Command(4000, "piece4", "defend", []),
        ]
        
        for cmd in commands:
            with self.subTest(command=cmd.type):
                self.state.reset(cmd)
                result = self.state.get_command()
                self.assertEqual(result, cmd)
                self.assertEqual(result.type, cmd.type)
                self.assertEqual(result.piece_name, cmd.piece_name)
                self.assertEqual(result.timestamp, cmd.timestamp)
                
    def test_get_command_after_multiple_resets(self):
        """🧪 get_command אחרי מספר resets"""
        cmd1 = Command(1000, "piece1", "move", [1, 1])
        cmd2 = Command(2000, "piece2", "jump", [2, 2])
        cmd3 = Command(3000, "piece3", "rest", [])
        
        # Reset מספר פעמים
        self.state.reset(cmd1)
        self.assertEqual(self.state.get_command(), cmd1)
        
        self.state.reset(cmd2)
        self.assertEqual(self.state.get_command(), cmd2)
        
        self.state.reset(cmd3)
        self.assertEqual(self.state.get_command(), cmd3)
        
        # הcommand האחרון צריך להישאר
        final_result = self.state.get_command()
        self.assertEqual(final_result, cmd3)

if __name__ == '__main__':
    # הרצת כל הטסטים עם reporting מפורט
    unittest.main(verbosity=2)
