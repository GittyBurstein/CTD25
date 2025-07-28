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
"""🏗️ tests לאתחול מחלקת Moves"""
    
    def setUp(self):
"""🔧 setup data for each test"""
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
"""🧪 initialization with valid file"""
        with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test_moves.txt"), self.board_dims)
                
# checking שהboard dimensions נשמרו נכון
                self.assertEqual(moves.board_height, 8)
                self.assertEqual(moves.board_width, 8)
                
# checking שהmove_deltas נטענו נכון
                expected_deltas = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)]
                self.assertEqual(moves.move_deltas, expected_deltas)
                
    def test_initialization_with_different_board_sizes(self):
"""🧪 initialization with גדלי board different"""
        board_sizes = [(4, 4), (6, 8), (10, 10), (12, 8)]
        
        for height, width in board_sizes:
            with self.subTest(height=height, width=width):
                with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
                    with patch('pathlib.Path.exists', return_value=True):
                        moves = Moves(pathlib.Path("test.txt"), (height, width))
                        
                        self.assertEqual(moves.board_height, height)
                        self.assertEqual(moves.board_width, width)
                        
    def test_initialization_file_not_exists(self):
"""🧪 initialization with file שלא קיים"""
        with patch('pathlib.Path.exists', return_value=False):
            moves = Moves(pathlib.Path("non_existent.txt"), self.board_dims)
            
# צריך לאתחל with list empty
            self.assertEqual(moves.move_deltas, [])
            self.assertEqual(moves.board_height, 8)
            self.assertEqual(moves.board_width, 8)


class TestMovesFileParsing(unittest.TestCase):
"""📄 tests לparsing movement files"""
    
    def setUp(self):
"""🔧 setup data"""
        self.board_dims = (8, 8)
        
    def test_parse_basic_moves(self):
"""🧪 ניתוח movements בסיסיות"""
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
"""🧪 ניתוח with lines הערות"""
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
"""🧪 parsing with empty lines"""
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
"""🧪 ניתוח with פורמט מיוחד (with :)"""
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
"""🧪 ניתוח with רווחים white"""
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
"""🧪 ignore invalid format lines"""
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
                
# only השורות התקינות צריכות להישמר
                expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                self.assertEqual(moves.move_deltas, expected)


class TestMovesGetMoves(unittest.TestCase):
"""🎯 tests לcalculate valid movements"""
    
    def setUp(self):
"""🔧 setup data"""
        self.board_dims = (8, 8)
# creating moves with movements בסיסיות
        basic_content = """1,0
-1,0
0,1
0,-1"""
        
        with patch('builtins.open', mock_open(read_data=basic_content)):
            with patch('pathlib.Path.exists', return_value=True):
                self.moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
    def test_get_moves_from_center(self):
"""🧪 חישוב movements ממרכז הלוח"""
# position (4,4) במרכז board 8x8
        valid_moves = self.moves.get_moves(4, 4)
        
        expected = [(5, 4), (3, 4), (4, 5), (4, 3)]  # כל הכיוונים תקינים
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
    def test_get_moves_from_top_left_corner(self):
"""🧪 חישוב movements מפינה שמאל עליון"""
        valid_moves = self.moves.get_moves(0, 0)
        
# only movements כלפי מטה וימין validity
        expected = [(1, 0), (0, 1)]
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
    def test_get_moves_from_bottom_right_corner(self):
"""🧪 חישוב movements מפינה ימין תחתון"""
        valid_moves = self.moves.get_moves(7, 7)
        
# only movements כלפי מעלה ושמאל validity
        expected = [(6, 7), (7, 6)]
        self.assertEqual(sorted(valid_moves), sorted(expected))
        
    def test_get_moves_from_edges(self):
"""🧪 חישוב movements מקצוות הלוח"""
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
"""🧪 position מחוץ ללוח עדיין מחשב movements שחוזרות ללוח"""
# הקוד no בודק if המיקום הראשוני valid, only if התוצאה valid
# positions מחוץ ללוח עדיין יכולים לתת movements validity
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
"""🐎 tests לcomplex movement patterns"""
    
    def setUp(self):
"""🔧 setup data"""
        self.board_dims = (8, 8)
        
    def test_knight_moves(self):
"""🧪 movements knight chess"""
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
                
# check ממרכז הלוח
                valid_moves = knight_moves.get_moves(4, 4)
                expected = [
                    (6, 5), (6, 3), (2, 5), (2, 3),  # 2 מעלה/מטה, 1 שמאל/ימין
                    (5, 6), (5, 2), (3, 6), (3, 2)   # 1 מעלה/מטה, 2 שמאל/ימין
                ]
                self.assertEqual(sorted(valid_moves), sorted(expected))
                
# check מפינה - part מהתנועות no validity
                valid_moves = knight_moves.get_moves(1, 1)
                expected = [(3, 2), (3, 0), (2, 3), (0, 3)]  # רק תנועות בתוך הלוח
                self.assertEqual(sorted(valid_moves), sorted(expected))
                
    def test_bishop_moves(self):
"""🧪 movements רץ (אלכסוניות)"""
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
                
# check ממרכז הלוח
                valid_moves = bishop_moves.get_moves(4, 4)
                expected = [
                    (5, 5), (5, 3), (3, 5), (3, 3),  # 1 אלכסון
                    (6, 6), (6, 2), (2, 6), (2, 2),  # 2 אלכסון
                    (7, 7), (7, 1), (1, 7), (1, 1)   # 3 אלכסון
                ]
                self.assertEqual(sorted(valid_moves), sorted(expected))
                
    def test_custom_large_moves(self):
"""🧪 movements גדולות מותאמות אישית"""
        large_content = """5,0
-5,0
0,5
0,-5
3,4
-3,-4"""
        
        with patch('builtins.open', mock_open(read_data=large_content)):
            with patch('pathlib.Path.exists', return_value=True):
                custom_moves = Moves(pathlib.Path("custom.txt"), self.board_dims)
                
# check ממרכז הלוח - only movements בתוך הלוח יהיו validity
                valid_moves = custom_moves.get_moves(4, 4)
# only (-5,0) נותן (4-5=-1) שזה מחוץ ללוח, אז only זה נדחה
# נבדוק which movements אכן validity:
# (4+5, 4+0) = (9,4) - מחוץ ללוח
# (4-5, 4+0) = (-1,4) - מחוץ ללוח
# (4+0, 4+5) = (4,9) - מחוץ ללוח
# (4+0, 4-5) = (4,-1) - מחוץ ללוח
# (4+3, 4+4) = (7,8) - מחוץ ללוח
# (4-3, 4-4) = (1,0) - בתוך הלוח!
                expected = [(1, 0)]  # רק תנועה אחת תקינה
                self.assertEqual(sorted(valid_moves), sorted(expected))


class TestMovesPathBlocking(unittest.TestCase):
"""🚧 tests לcheck path blocking"""
    
    def setUp(self):
"""🔧 setup data"""
        self.board_dims = (8, 8)
        
    def test_knight_path_not_blocked(self):
"""🧪 knight אינו נחסם על ידי pieces אחרים"""
# creating state with pieces רבים
        mock_pieces = {
            "piece1": Mock(),
            "piece2": Mock(),
            "piece3": Mock()
        }
        
# הגדרת מיקומי pieces
        mock_pieces["piece1"].current_state.physics.current_cell = (3, 3)
        mock_pieces["piece2"].current_state.physics.current_cell = (3, 4)
        mock_pieces["piece3"].current_state.physics.current_cell = (4, 3)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
# knight יכול לקפוץ מעל pieces
                is_blocked = moves.is_path_blocked((2, 2), (4, 3), "N", mock_pieces)
                self.assertFalse(is_blocked)
                
    def test_rook_path_blocked(self):
"""🧪 rook נחסם על ידי piece בנתיב"""
        mock_pieces = {
            "blocking_piece": Mock()
        }
        
# piece חוסם בנתיב
        mock_pieces["blocking_piece"].current_state.physics.current_cell = (2, 3)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
# rook נחסם
                is_blocked = moves.is_path_blocked((2, 2), (2, 5), "R", mock_pieces)
                self.assertTrue(is_blocked)
                
    def test_rook_path_not_blocked(self):
"""🧪 rook no נחסם כשהנתיב free"""
        mock_pieces = {
            "other_piece": Mock()
        }
        
# piece no בנתיב
        mock_pieces["other_piece"].current_state.physics.current_cell = (5, 5)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
# rook no נחסם
                is_blocked = moves.is_path_blocked((2, 2), (2, 5), "R", mock_pieces)
                self.assertFalse(is_blocked)
                
    def test_bishop_diagonal_blocked(self):
"""🧪 רץ נחסם באלכסון"""
        mock_pieces = {
            "blocking_piece": Mock()
        }
        
# piece חוסם באלכסון
        mock_pieces["blocking_piece"].current_state.physics.current_cell = (3, 3)
        
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), self.board_dims)
                
# רץ נחסם באלכסון
                is_blocked = moves.is_path_blocked((2, 2), (4, 4), "B", mock_pieces)
                self.assertTrue(is_blocked)


class TestMovesEdgeCases(unittest.TestCase):
"""🎯 tests למקרי קצה"""
    
    def setUp(self):
"""🔧 setup data"""
        self.board_dims = (8, 8)
        
    def test_empty_move_file(self):
"""🧪 file movements empty"""
        with patch('builtins.open', mock_open(read_data="")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("empty.txt"), self.board_dims)
                
                self.assertEqual(moves.move_deltas, [])
                
# checking שget_moves מחזיר list empty
                valid_moves = moves.get_moves(4, 4)
                self.assertEqual(valid_moves, [])
                
    def test_single_move_file(self):
"""🧪 file with movement one בלבד"""
        with patch('builtins.open', mock_open(read_data="1,0")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("single.txt"), self.board_dims)
                
                self.assertEqual(moves.move_deltas, [(1, 0)])
                
                valid_moves = moves.get_moves(4, 4)
                self.assertEqual(valid_moves, [(5, 4)])
                
    def test_board_size_1x1(self):
"""🧪 board בגודל 1x1"""
        with patch('builtins.open', mock_open(read_data="1,0\n0,1")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), (1, 1))
                
# all התנועות צריכות להיות מחוץ ללוח
                valid_moves = moves.get_moves(0, 0)
                self.assertEqual(valid_moves, [])
                
    def test_very_large_board(self):
"""🧪 board גדול very"""
        large_board = (100, 100)
        
        with patch('builtins.open', mock_open(read_data="10,10\n-10,-10")):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test.txt"), large_board)
                
# movements צריכות לעבוד בלוח גדול
                valid_moves = moves.get_moves(50, 50)
                expected = [(60, 60), (40, 40)]
                self.assertEqual(sorted(valid_moves), sorted(expected))


if __name__ == '__main__':
print("🧪 running tests comprehensive for class Moves...")
    print("=" * 60)
    unittest.main(verbosity=2)
