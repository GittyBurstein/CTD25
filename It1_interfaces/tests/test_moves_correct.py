#!/usr/bin/env python3
"""
🧪 טסטים מקיפים למחלקת Moves - גרסה מתוקנת
בדיקת כל פונקציונליות ניהול תנועות כלי שחמט עם API נכון
"""
import unittest
from unittest.mock import Mock, patch, mock_open
import sys
import os
import pathlib
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Moves import Moves


class TestMovesInitialization(unittest.TestCase):
    """🏗️ טסטים לאתחול מחלקת Moves"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.test_moves_content = """# Test moves file
1,0
-1,0
0,1
0,-1
2,2
-2,-2
"""
        self.board_dims = (8, 8)  # לוח שחמט סטנדרטי
        
    def test_initialization_with_valid_file(self):
        """🧪 אתחול עם קובץ תקין"""
        with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test_moves.txt"), self.board_dims)
                
                # בדיקת שהboard dimensions נשמרו נכון
                self.assertEqual(moves.board_height, 8)
                self.assertEqual(moves.board_width, 8)
                
                # בדיקת שהmove_deltas נטענו נכון
                expected_deltas = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)]
                self.assertEqual(moves.move_deltas, expected_deltas)
                
    def test_initialization_with_different_board_sizes(self):
        """🧪 אתחול עם גדלי לוח שונים"""
        board_sizes = [(4, 4), (6, 8), (10, 10), (12, 8)]
        
        for height, width in board_sizes:
            with self.subTest(height=height, width=width):
                with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
                    with patch('pathlib.Path.exists', return_value=True):
                        moves = Moves(pathlib.Path("test.txt"), (height, width))
                        
                        self.assertEqual(moves.board_height, height)
                        self.assertEqual(moves.board_width, width)
                        
    def test_initialization_file_not_exists(self):
        """🧪 אתחול עם קובץ שלא קיים"""
        with patch('pathlib.Path.exists', return_value=False):
            moves = Moves(pathlib.Path("non_existent.txt"), self.board_dims)
            
            # צריך לאתחל עם רשימה ריקה
            self.assertEqual(moves.move_deltas, [])
            self.assertEqual(moves.board_height, 8)
            self.assertEqual(moves.board_width, 8)


class TestMovesFileParsing(unittest.TestCase):
    """📄 טסטים לניתוח קבצי תנועות"""
    
    def setUp(self):
        """🔧 הכנת נתונים"""
        self.board_dims = (8, 8)
        
    def test_parse_basic_moves(self):
        """🧪 ניתוח תנועות בסיסיות"""
        content = """1,0
-1,0
0,1
0,-1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                self.assertEqual(moves.move_deltas, expected)
                
    def test_parse_with_comments(self):
        """🧪 ניתוח עם שורות הערות"""
        content = """# This is a comment
1,0
# Another comment
-1,0
0,1
0,-1
# Final comment"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                self.assertEqual(moves.move_deltas, expected)
                
    def test_parse_with_empty_lines(self):
        """🧪 ניתוח עם שורות ריקות"""
        content = """1,0

-1,0


0,1
0,-1

"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                self.assertEqual(moves.move_deltas, expected)
                
    def test_parse_with_special_format(self):
        """🧪 ניתוח עם פורמט מיוחד (עם :)"""
        content = """1,0:capture
-1,0:non_capture
0,1:special
0,-1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                # צריך להתעלם מהחלק אחרי :
                expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                self.assertEqual(moves.move_deltas, expected)
                
    def test_parse_with_whitespace(self):
        """🧪 ניתוח עם רווחים לבנים"""
        content = """  1,0  
 -1 , 0 
0, 1  
 0 , -1 """
        
        with patch('builtins.open', mock_open(read_data=content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                self.assertEqual(moves.move_deltas, expected)
                
    def test_parse_invalid_format_lines_skipped(self):
        """🧪 שורות בפורמט לא תקין מתעלמים מהן"""
        content = """1,0
invalid_line
-1,0
not,a,number
0,1
too_few_parts
0,-1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                # רק השורות התקינות צריכות להישמר
                expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                self.assertEqual(moves.move_deltas, expected)


class TestMovesGetMoves(unittest.TestCase):
    """🎯 טסטים לחישוב תנועות תקינות"""
    
    def setUp(self):
        """🔧 הכנת נתונים"""
        self.board_dims = (8, 8)
        # יצירת moves עם תנועות בסיסיות
        basic_content = """1,0
-1,0
0,1
0,-1"""
        
        with patch('builtins.open', mock_open(read_data=basic_content)):
            with patch('pathlib.Path.exists', return_value=True):
                self.moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
    def test_get_moves_from_center(self):
        """🧪 חישוב תנועות ממרכז הלוח"""
        # מיקום (4,4) במרכז לוח 8x8
        valid_moves = self.moves.get_moves(4, 4)
        
        expected = [(5, 4), (3, 4), (4, 5), (4, 3)]  # כל הכיוונים תקינים
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
    def test_get_moves_from_top_left_corner(self):
        """🧪 חישוב תנועות מפינה שמאל עליון"""
        valid_moves = self.moves.get_moves(0, 0)
        
        # רק תנועות כלפי מטה וימין תקינות
        expected = [(1, 0), (0, 1)]
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
    def test_get_moves_from_bottom_right_corner(self):
        """🧪 חישוב תנועות מפינה ימין תחתון"""
        valid_moves = self.moves.get_moves(7, 7)
        
        # רק תנועות כלפי מעלה ושמאל תקינות
        expected = [(6, 7), (7, 6)]
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
    def test_get_moves_from_edges(self):
        """🧪 חישוב תנועות מקצוות הלוח"""
        # קצה עליון
        valid_moves = self.moves.get_moves(0, 4)
        expected = [(1, 4), (0, 5), (0, 3)]  # לא יכול לעלות
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
        # קצה תחתון
        valid_moves = self.moves.get_moves(7, 4)
        expected = [(6, 4), (7, 5), (7, 3)]  # לא יכול לרדת
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
        # קצה שמאל
        valid_moves = self.moves.get_moves(4, 0)
        expected = [(5, 0), (3, 0), (4, 1)]  # לא יכול לשמאל
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
        # קצה ימין
        valid_moves = self.moves.get_moves(4, 7)
        expected = [(5, 7), (3, 7), (4, 6)]  # לא יכול ימינה
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
    def test_get_moves_outside_board_returns_valid_moves(self):
        """🧪 מיקום מחוץ ללוח עדיין מחשב תנועות שחוזרות ללוח"""
        # הקוד לא בודק אם המיקום הראשוני תקין, רק אם התוצאה תקינה
        # מיקומים מחוץ ללוח עדיין יכולים לתת תנועות תקינות
        test_cases = [
            ((-1, 0), [(0, 0)]),  # מחוץ ללוח למעלה, תנועה (1,0) נותנת (0,0)
            ((0, -1), [(0, 0)]),  # מחוץ ללוח לשמאל, תנועה (0,1) נותנת (0,0)
            ((8, 0), [(7, 0)]),   # מחוץ ללוח למטה, תנועה (-1,0) נותנת (7,0)
            ((0, 8), [(0, 7)]),   # מחוץ ללוח לימין, תנועה (0,-1) נותנת (0,7)
        ]
        
        for (row, col), expected in test_cases:
            with self.subTest(row=row, col=col):
                valid_moves = self.moves.get_moves(row, col)
                self.assertEqual(sorted(valid_moves), sorted(expected))


class TestMovesComplexPatterns(unittest.TestCase):
    """🐎 טסטים לתבניות תנועה מורכבות"""
    
    def setUp(self):
        """🔧 הכנת נתונים"""
        self.board_dims = (8, 8)
        
    def test_knight_moves(self):
        """🧪 תנועות סוס שחמט"""
        knight_content = """2,1
2,-1
-2,1
-2,-1
1,2
1,-2
-1,2
-1,-2"""
        
        with patch('builtins.open', mock_open(read_data=knight_content)):
            with patch('pathlib.Path.exists', return_value=True):
                knight_moves = Moves(pathlib.Path("knight.txt"), self.board_dims)
                
                # בדיקה ממרכז הלוח
                valid_moves = knight_moves.get_moves(4, 4)
                expected = [
                    (6, 5), (6, 3), (2, 5), (2, 3),  # 2 מעלה/מטה, 1 שמאל/ימין
                    (5, 6), (5, 2), (3, 6), (3, 2)   # 1 מעלה/מטה, 2 שמאל/ימין
                ]
                self.assertEqual(sorted(valid_moves), sorted(expected))
                
                # בדיקה מפינה - חלק מהתנועות לא תקינות
                valid_moves = knight_moves.get_moves(1, 1)
                expected = [(3, 2), (3, 0), (2, 3), (0, 3)]  # רק תנועות בתוך הלוח
                self.assertEqual(sorted(valid_moves), sorted(expected))
                
    def test_bishop_moves(self):
        """🧪 תנועות רץ (אלכסוניות)"""
        bishop_content = """1,1
1,-1
-1,1
-1,-1
2,2
2,-2
-2,2
-2,-2
3,3
3,-3
-3,3
-3,-3"""
        
        with patch('builtins.open', mock_open(read_data=bishop_content)):
            with patch('pathlib.Path.exists', return_value=True):
                bishop_moves = Moves(pathlib.Path("bishop.txt"), self.board_dims)
                
                # בדיקה ממרכז הלוח
                valid_moves = bishop_moves.get_moves(4, 4)
                expected = [
                    (5, 5), (5, 3), (3, 5), (3, 3),  # 1 אלכסון
                    (6, 6), (6, 2), (2, 6), (2, 2),  # 2 אלכסון
                    (7, 7), (7, 1), (1, 7), (1, 1)   # 3 אלכסון
                ]
                self.assertEqual(sorted(valid_moves), sorted(expected))
                
    def test_custom_large_moves(self):
        """🧪 תנועות גדולות מותאמות אישית"""
        large_content = """5,0
-5,0
0,5
0,-5
3,4
-3,-4"""
        
        with patch('builtins.open', mock_open(read_data=large_content)):
            with patch('pathlib.Path.exists', return_value=True):
                custom_moves = Moves(pathlib.Path("custom.txt"), self.board_dims)
                
                # בדיקה ממרכז הלוח - רק תנועות בתוך הלוח יהיו תקינות
                valid_moves = custom_moves.get_moves(4, 4)
                # רק (-5,0) נותן (4-5=-1) שזה מחוץ ללוח, אז רק זה נדחה
                # נבדוק איזה תנועות אכן תקינות:
                # (4+5, 4+0) = (9,4) - מחוץ ללוח
                # (4-5, 4+0) = (-1,4) - מחוץ ללוח  
                # (4+0, 4+5) = (4,9) - מחוץ ללוח
                # (4+0, 4-5) = (4,-1) - מחוץ ללוח
                # (4+3, 4+4) = (7,8) - מחוץ ללוח
                # (4-3, 4-4) = (1,0) - בתוך הלוח!
                expected = [(1, 0)]  # רק תנועה אחת תקינה
                self.assertEqual(sorted(valid_moves), sorted(expected))


class TestMovesPathBlocking(unittest.TestCase):
    """🚧 טסטים לבדיקת חסימת נתיבים"""
    
    def setUp(self):
        """🔧 הכנת נתונים"""
        self.board_dims = (8, 8)
        
    def test_knight_path_not_blocked(self):
        """🧪 סוס אינו נחסם על ידי כלים אחרים"""
        # יצירת מצב עם כלים רבים
        mock_pieces = {
            "piece1": Mock(),
            "piece2": Mock(),
            "piece3": Mock()
        }
        
        # הגדרת מיקומי כלים
        mock_pieces["piece1"].current_state.physics.current_cell = (3, 3)
        mock_pieces["piece2"].current_state.physics.current_cell = (3, 4)
        mock_pieces["piece3"].current_state.physics.current_cell = (4, 3)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                # סוס יכול לקפוץ מעל כלים
                is_blocked = moves.is_path_blocked((2, 2), (4, 3), "N", mock_pieces)
                self.assertFalse(is_blocked)
                
    def test_rook_path_blocked(self):
        """🧪 צריח נחסם על ידי כלי בנתיב"""
        mock_pieces = {
            "blocking_piece": Mock()
        }
        
        # כלי חוסם בנתיב
        mock_pieces["blocking_piece"].current_state.physics.current_cell = (2, 3)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                # צריח נחסם
                is_blocked = moves.is_path_blocked((2, 2), (2, 5), "R", mock_pieces)
                self.assertTrue(is_blocked)
                
    def test_rook_path_not_blocked(self):
        """🧪 צריח לא נחסם כשהנתיב פנוי"""
        mock_pieces = {
            "other_piece": Mock()
        }
        
        # כלי לא בנתיב
        mock_pieces["other_piece"].current_state.physics.current_cell = (5, 5)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                # צריח לא נחסם
                is_blocked = moves.is_path_blocked((2, 2), (2, 5), "R", mock_pieces)
                self.assertFalse(is_blocked)
                
    def test_bishop_diagonal_blocked(self):
        """🧪 רץ נחסם באלכסון"""
        mock_pieces = {
            "blocking_piece": Mock()
        }
        
        # כלי חוסם באלכסון
        mock_pieces["blocking_piece"].current_state.physics.current_cell = (3, 3)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
                # רץ נחסם באלכסון
                is_blocked = moves.is_path_blocked((2, 2), (4, 4), "B", mock_pieces)
                self.assertTrue(is_blocked)


class TestMovesEdgeCases(unittest.TestCase):
    """🎯 טסטים למקרי קצה"""
    
    def setUp(self):
        """🔧 הכנת נתונים"""
        self.board_dims = (8, 8)
        
    def test_empty_move_file(self):
        """🧪 קובץ תנועות ריק"""
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("empty.txt"), self.board_dims)
                
                self.assertEqual(moves.move_deltas, [])
                
                # בדיקת שget_moves מחזיר רשימה ריקה
                valid_moves = moves.get_moves(4, 4)
                self.assertEqual(valid_moves, [])
                
    def test_single_move_file(self):
        """🧪 קובץ עם תנועה אחת בלבד"""
        with patch('builtins.open', mock_open(read_data="1,0")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("single.txt"), self.board_dims)
                
                self.assertEqual(moves.move_deltas, [(1, 0)])
                
                valid_moves = moves.get_moves(4, 4)
                self.assertEqual(valid_moves, [(5, 4)])
                
    def test_board_size_1x1(self):
        """🧪 לוח בגודל 1x1"""
        with patch('builtins.open', mock_open(read_data="1,0\n0,1")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), (1, 1))
                
                # כל התנועות צריכות להיות מחוץ ללוח
                valid_moves = moves.get_moves(0, 0)
                self.assertEqual(valid_moves, [])
                
    def test_very_large_board(self):
        """🧪 לוח גדול מאוד"""
        large_board = (100, 100)
        
        with patch('builtins.open', mock_open(read_data="10,10\n-10,-10")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), large_board)
                
                # תנועות צריכות לעבוד בלוח גדול
                valid_moves = moves.get_moves(50, 50)
                expected = [(60, 60), (40, 40)]
                self.assertEqual(sorted(valid_moves), sorted(expected))


if __name__ == '__main__':
    print("🧪 מריץ טסטים מקיפים למחלקת Moves...")
    print("=" * 60)
    unittest.main(verbosity=2)
