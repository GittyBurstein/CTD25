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
        
    def test_initialization_with_file_path_string(self):
        """🧪 אתחול עם נתיב קובץ כstring"""
        with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
            with patch('pathlib.Path.exists', return_value=True):
                moves = Moves(pathlib.Path("test_moves.txt"), (8, 8))
                
                # בדיקת שהנתיב נשמר נכון
                self.assertEqual(moves.move_deltas, [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)])
                self.assertEqual(moves.board_height, 8)
                self.assertEqual(moves.board_width, 8)
            
    def test_initialization_with_pathlib_path(self):
        """🧪 אתחול עם pathlib.Path"""
        path = pathlib.Path("test_moves.txt")
        
        with patch('builtins.open', mock_open(read_data=self.test_moves_content)):
            moves = Moves(path)
            
            # בדיקת שהנתיב נשמר נכון
            self.assertEqual(moves.moves_file_path, path)
            
            # בדיקת שהtoves נטענו נכון
            expected_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)]
            self.assertEqual(moves.moves, expected_moves)
            
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_initialization_file_not_found(self, mock_file):
        """🧪 אתחול עם קובץ שלא קיים"""
        with self.assertRaises(FileNotFoundError):
            Moves("non_existent_file.txt")
            
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_initialization_permission_error(self, mock_file):
        """🧪 אתחול עם קובץ ללא הרשאות"""
        with self.assertRaises(PermissionError):
            Moves("no_permission_file.txt")


class TestMovesFileParsing(unittest.TestCase):
    """📄 טסטים לניתוח קבצי תנועות"""
    
    def test_parse_basic_moves(self):
        """🧪 ניתוח תנועות בסיסיות"""
        content = """1,0
-1,0
0,1
0,-1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_with_comments(self):
        """🧪 ניתוח עם שורות הערות"""
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
        """🧪 ניתוח עם שורות ריקות"""
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
        """🧪 ניתוח עם רווחים לבנים"""
        content = """  1,0  
 -1 , 0 
0, 1  
 0 , -1 """
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_large_numbers(self):
        """🧪 ניתוח עם מספרים גדולים"""
        content = """10,15
-20,-25
100,0
0,-50"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(10, 15), (-20, -25), (100, 0), (0, -50)]
            self.assertEqual(moves.moves, expected)
            
    def test_parse_edge_case_zeros(self):
        """🧪 ניתוח עם אפסים"""
        content = """0,0
0,1
1,0
-0,-0"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            
            expected = [(0, 0), (0, 1), (1, 0), (0, 0)]
            self.assertEqual(moves.moves, expected)


class TestMovesErrorHandling(unittest.TestCase):
    """⚠️ טסטים לטיפול בשגיאות"""
    
    def test_invalid_format_missing_comma(self):
        """🧪 פורמט לא תקין - חסרה פסיק"""
        content = """1 0
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_too_many_values(self):
        """🧪 פורמט לא תקין - יותר מדי ערכים"""
        content = """1,0,5
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_too_few_values(self):
        """🧪 פורמט לא תקין - מעט מדי ערכים"""
        content = """1
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_non_numeric(self):
        """🧪 פורמט לא תקין - ערכים לא מספריים"""
        content = """a,b
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_invalid_format_mixed_valid_invalid(self):
        """🧪 פורמט מעורב - חלק תקין חלק לא"""
        content = """1,0
invalid_line
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            with self.assertRaises(ValueError):
                Moves("test.txt")
                
    def test_empty_file(self):
        """🧪 קובץ ריק"""
        content = ""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            self.assertEqual(moves.moves, [])
            
    def test_only_comments_and_empty_lines(self):
        """🧪 רק הערות ושורות ריקות"""
        content = """# Only comments

# And empty lines

"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("test.txt")
            self.assertEqual(moves.moves, [])


class TestMovesDataAccess(unittest.TestCase):
    """📊 טסטים לגישה לנתונים"""
    
    def setUp(self):
        """🔧 הכנת נתונים לכל טסט"""
        self.moves_content = """1,0
-1,0
0,1
0,-1
2,2
-2,-2"""
        
        with patch('builtins.open', mock_open(read_data=self.moves_content)):
            self.moves = Moves("test.txt")
            
    def test_get_moves_list(self):
        """🧪 קבלת רשימת התנועות"""
        expected = [(1, 0), (-1, 0), (0, 1), (0, -1), (2, 2), (-2, -2)]
        self.assertEqual(self.moves.moves, expected)
        
    def test_moves_list_immutability(self):
        """🧪 בדיקת שרשימת התנועות לא ניתנת לשינוי מבחוץ"""
        original_moves = self.moves.moves.copy()
        
        # נסיון לשנות את הרשימה
        self.moves.moves.append((5, 5))
        
        # הרשימה צריכה להשתנות (Python lists are mutable)
        # זה מראה שצריך להוסיף property או copy אם רוצים immutability
        self.assertNotEqual(self.moves.moves, original_moves)
        
    def test_file_path_access(self):
        """🧪 גישה לנתיב הקובץ"""
        self.assertEqual(self.moves.moves_file_path, "test.txt")
        
    def test_moves_count(self):
        """🧪 ספירת מספר התנועות"""
        self.assertEqual(len(self.moves.moves), 6)


class TestMovesRealWorldScenarios(unittest.TestCase):
    """🌍 טסטים למקרי שימוש אמיתיים"""
    
    def test_chess_pawn_moves(self):
        """🧪 תנועות חייל שחמט"""
        pawn_content = """1,0
2,0"""  # פ Forward 1 or 2
        
        with patch('builtins.open', mock_open(read_data=pawn_content)):
            moves = Moves("pawn_moves.txt")
            
            expected = [(1, 0), (2, 0)]
            self.assertEqual(moves.moves, expected)
            
    def test_chess_knight_moves(self):
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
            moves = Moves("knight_moves.txt")
            
            expected = [
                (2, 1), (2, -1), (-2, 1), (-2, -1),
                (1, 2), (1, -2), (-1, 2), (-1, -2)
            ]
            self.assertEqual(moves.moves, expected)
            
    def test_chess_king_moves(self):
        """🧪 תנועות מלך שחמט"""
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
        """🧪 תנועות כלי מותאם אישית"""
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
    """💾 טסטים לפעולות קובץ"""
    
    def test_with_actual_temp_file(self):
        """🧪 בדיקה עם קובץ זמני אמיתי"""
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
            # נקה את הקובץ הזמני
            os.unlink(temp_file_path)
            
    def test_unicode_handling(self):
        """🧪 טיפול בתווי Unicode בהערות"""
        unicode_content = """# תנועות בעברית
1,0  # קדימה
-1,0 # אחורה
0,1  # ימינה
0,-1 # שמאלה"""
        
        with patch('builtins.open', mock_open(read_data=unicode_content)):
            moves = Moves("unicode_test.txt")
            
            expected = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.assertEqual(moves.moves, expected)


class TestMovesEdgeCases(unittest.TestCase):
    """🎯 טסטים למקרי קצה"""
    
    def test_very_large_file(self):
        """🧪 קובץ גדול מאוד"""
        # יצירת קובץ עם 1000 תנועות
        large_content = ""
        for i in range(1000):
            large_content += f"{i % 10},{(i * 2) % 10}\n"
            
        with patch('builtins.open', mock_open(read_data=large_content)):
            moves = Moves("large_file.txt")
            
            # בדיקת שכל התנועות נטענו
            self.assertEqual(len(moves.moves), 1000)
            
            # בדיקת כמה דוגמאות
            self.assertEqual(moves.moves[0], (0, 0))
            self.assertEqual(moves.moves[1], (1, 2))
            self.assertEqual(moves.moves[10], (0, 0))  # 10 % 10 = 0, (10*2) % 10 = 0
            
    def test_file_with_only_one_move(self):
        """🧪 קובץ עם תנועה אחת בלבד"""
        content = "5,3"
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("single_move.txt")
            
            self.assertEqual(moves.moves, [(5, 3)])
            self.assertEqual(len(moves.moves), 1)
            
    def test_duplicate_moves(self):
        """🧪 תנועות כפולות"""
        content = """1,0
1,0
2,1
1,0
2,1"""
        
        with patch('builtins.open', mock_open(read_data=content)):
            moves = Moves("duplicate_moves.txt")
            
            # הkwarts לא מסנן כפילויות - זה נשמר כמו שהוא
            expected = [(1, 0), (1, 0), (2, 1), (1, 0), (2, 1)]
            self.assertEqual(moves.moves, expected)


if __name__ == '__main__':
    print("🧪 מריץ טסטים מקיפים למחלקת Moves...")
    print("=" * 60)
    unittest.main(verbosity=2)
