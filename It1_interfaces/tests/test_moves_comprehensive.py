#!/usr/bin/env python3
"""
🧪 טסטים מקיפים למחלקת Moves
בדיקת כל פונקציונליות ניהול תנועות כלי שחמט
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
        
    def test_initialization_with_file_path_string(self):
"""🧪 initialization with path file כstring"""
        with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test_moves.txt"), (8, 8))
                
# checking שהנתיב נשמר נכון
                self.assertEqual(moves.move_deltas, [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)])
                self.assertEqual(moves.board_height, 8)
                self.assertEqual(moves.board_width, 8)
            
    def test_initialization_with_pathlib_path(self):
"""🧪 initialization with pathlib.Path"""
        path = pathlib.Path("test_moves.txt")
        
        with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
            moves = Moves(path)
            
# checking שהנתיב נשמר נכון
            self.assertEqual(moves.moves_file_path, path)
            
# checking שהtoves נטענו נכון
            expected_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)]
            self.assertEqual(moves.moves, expected_moves)
            
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_initialization_file_not_found(self, mock_file):
"""🧪 initialization with file שלא קיים"""
        with self.assertRaises(FileNotFoundError):
            Moves("non_existent_file.txt")
            
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_initialization_permission_error(self, mock_file):
"""🧪 initialization with file ללא הרשאות"""
        with self.assertRaises(PermissionError):
            Moves("no_permission_file.txt")


class TestMovesFileParsing(unittest.TestCase):
"""📄 tests לparsing movement files"""
    
    def test_parse_basic_moves(self):
"""🧪 ניתוח movements בסיסיות"""
        content = """1,0
-1,0
0,1
0,-1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_with_comments(self):
"""🧪 ניתוח with lines הערות"""
        content = """# This is a comment
1,0
# Another comment
-1,0
0,1  # Inline comment
0,-1
# Final comment"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_with_empty_lines(self):
"""🧪 parsing with empty lines"""
        content = """1,0

-1,0


0,1
0,-1

"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_with_whitespace(self):
"""🧪 ניתוח with רווחים white"""
        content = """  1,0  
 -1 , 0 
0, 1  
 0 , -1 """
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_large_numbers(self):
"""🧪 ניתוח with numbers גדולים"""
        content = """10,15
-20,-25
100,0
0,-50"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(10, 15), (-20, -25), (100, 0), (0, -50)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_edge_case_zeros(self):
"""🧪 ניתוח with אפסים"""
        content = """0,0
0,1
1,0
-0,-0"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(0, 0), (0, 1), (1, 0), (0, 0)]
            self.assertEqual(moves.moves, expected)


class TestMovesErrorHandling(unittest.TestCase):
"""⚠️ tests לטיפול בשגיאות"""
    
    def test_invalid_format_missing_comma(self):
"""🧪 פורמט no valid - חסרה פסיק"""
        content = """1 0
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_too_many_values(self):
"""🧪 פורמט no valid - more מדי ערכים"""
        content = """1,0,5
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_too_few_values(self):
"""🧪 פורמט no valid - few מדי ערכים"""
        content = """1
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_non_numeric(self):
"""🧪 פורמט no valid - ערכים no מספריים"""
        content = """a,b
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_mixed_valid_invalid(self):
"""🧪 פורמט מעורב - part valid part no"""
        content = """1,0
invalid_line
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_empty_file(self):
"""🧪 file empty"""
        content = ""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            self.assertEqual(moves.moves, [])
            
    def test_only_comments_and_empty_lines(self):
"""🧪 only הערות ושורות ריקות"""
        content = """# Only comments

# And empty lines

"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            self.assertEqual(moves.moves, [])


class TestMovesDataAccess(unittest.TestCase):
"""📊 tests לגישה לנתונים"""
    
    def setUp(self):
"""🔧 setup data for each test"""
        self.moves_content = """1,0
-1,0
0,1
0,-1
2,2
-2,-2"""
        
        with patch('builtins.open', mock_open(read_data=self.moves_content)):
            self.moves = Moves("test.txt")
            
    def test_get_moves_list(self):
"""🧪 getting רשימת התנועות"""
        expected = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)]
        self.assertEqual(self.moves.moves, expected)
        
    def test_moves_list_immutability(self):
"""🧪 checking שרשימת התנועות no ניתנת לשינוי מבחוץ"""
        original_moves = self.moves.moves.copy()
        
# נסיון לשנות the הרשימה
        self.moves.moves.append((5, 5))
        
# הרשימה צריכה להשתנות (Python lists are mutable)
# זה מראה שצריך להוסיף property or copy if רוצים immutability
        self.assertNotEqual(self.moves.moves, original_moves)
        
    def test_file_path_access(self):
"""🧪 גישה לנתיב הקובץ"""
        self.assertEqual(self.moves.moves_file_path, "test.txt")
        
    def test_moves_count(self):
"""🧪 ספירת number התנועות"""
        self.assertEqual(len(self.moves.moves), 6)


class TestMovesRealWorldScenarios(unittest.TestCase):
"""🌍 tests למקרי שימוש אמיתיים"""
    
    def test_chess_pawn_moves(self):
"""🧪 movements חייל chess"""
        pawn_content = """1,0
2,0""" # פ Forward 1 or 2
        
        with patch('builtins.open', mock_open(read_data=pawn_content)):
            moves = Moves("pawn_moves.txt")
            
            expected = [(1, 0), (2, 0)]
            self.assertEqual(moves.moves, expected)
            
    def test_chess_knight_moves(self):
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
            moves = Moves("knight_moves.txt")
            
            expected = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)
            ]
            self.assertEqual(moves.moves, expected)
            
    def test_chess_king_moves(self):
"""🧪 movements king chess"""
        king_content = """1,0
-1,0
0,1
0,-1
1,1
1,-1
-1,1
-1,-1"""
        
        with patch('builtins.open', mock_open(read_data=king_content)):
            moves = Moves("king_moves.txt")
            
            expected = [
                (1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
            self.assertEqual(moves.moves, expected)
            
    def test_custom_piece_moves(self):
"""🧪 movements piece מותאם אישית"""
        custom_content = """3,0
-3,0
0,3
0,-3
2,2
-2,-2
2,-2
-2,2"""
        
        with patch('builtins.open', mock_open(read_data=custom_content)):
            moves = Moves("custom_moves.txt")
            
            expected = [
                (3, 0), (-3, 0), (0, 3), (0, -3),
                (2, 2), (-2, -2), (2, -2), (-2, 2)
            ]
            self.assertEqual(moves.moves, expected)


class TestMovesFileIO(unittest.TestCase):
"""💾 tests לפעולות file"""
    
    def test_with_actual_temp_file(self):
"""🧪 check with file זמני אמיתי"""
        moves_content = """# Temporary test file
1,0
-1,0
0,1
0,-1"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(moves_content)
            temp_file_path = temp_file.name
            
        try:
# טען מהקובץ הזמני
            moves = Moves(temp_file_path)
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)
            
        finally:
# נקה the הקובץ הזמני
            os.unlink(temp_file_path)
            
    def test_unicode_handling(self):
"""🧪 טיפול בתווי Unicode בהערות"""
unicode_content = """# movements בעברית
1,0  # קדימה
-1,0 # אחורה
0,1  # ימינה
0,-1 # שמאלה"""
        
        with patch('builtins.open', mock_open(read_data=unicode_content)):
            moves = Moves("unicode_test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)


class TestMovesEdgeCases(unittest.TestCase):
"""🎯 tests למקרי קצה"""
    
    def test_very_large_file(self):
"""🧪 file גדול very"""
# creating file with 1000 movements
        large_content = ""
        for i in range(1000):
            large_content += f"{i % 10},{(i * 2) % 10}\n"
            
        with patch('builtins.open', mock_open(read_data=large_content)):
            moves = Moves("large_file.txt")
            
# checking שכל התנועות נטענו
            self.assertEqual(len(moves.moves), 1000)
            
# checking several דוגמאות
            self.assertEqual(moves.moves[0], (0, 0))
            self.assertEqual(moves.moves[1], (1, 2))
            self.assertEqual(moves.moves[10], (0, 0))  # 10 % 10 = 0, (10*2) % 10 = 0
            
    def test_file_with_only_one_move(self):
"""🧪 file with movement one בלבד"""
        content = "5,3"
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("single_move.txt")
            
            self.assertEqual(moves.moves, [(5, 3)])
            self.assertEqual(len(moves.moves), 1)
            
    def test_duplicate_moves(self):
"""🧪 movements כפולות"""
        content = """1,0
1,0
2,1
1,0
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("duplicate_moves.txt")
            
# הkwarts no מסנן כפילויות - זה נשמר כמו שהוא
            expected = [(1, 0), (1, 0), (2, 1), (1, 0), (2, 1)]
            self.assertEqual(moves.moves, expected)


if __name__ == '__main__':
print("🧪 running tests comprehensive for class Moves...")
    print("=" * 60)
    unittest.main(verbosity=2)
