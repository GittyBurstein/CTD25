# 🧪 מערכת הטסטים - Test Suite

## סקירה כללית

תיקייה זו מכילה מערכת טסטים מקיפה לפרויקט השחמט. המערכת כוללת טסטים לכל המחלקות הראשיות עם דגש על שימוש במוקים (mocks) למניעת תלות ברכיבים חיצוניים.

## 📁 מבנה התיקייה

```
tests/
├── run_tests.py                    # 🚀 מריץ הטסטים הראשי
├── test_command.py                 # 🧪 טסטים למחלקת Command
├── test_game.py                    # 🧪 טסטים למחלקת Game
├── test_threaded_input_manager.py  # 🧪 טסטים ל-ThreadedInputManager
├── test_physics.py                 # 🧪 טסטים למחלקת Physics
├── test_graphics.py                # 🧪 טסטים למחלקת Graphics
├── test_state.py                   # 🧪 טסטים למחלקת State
├── test_board.py                   # 🧪 טסטים למחלקת Board
├── test_piece.py                   # 🧪 טסטים למחלקת Piece
├── test_mock_img.py               # 🧪 טסטים למחלקת MockImg
└── README.md                       # 📖 המדריך הזה
```

## 🚀 הרצת הטסטים

### הרצת כל הטסטים
```bash
python tests/run_tests.py
```

### הרצת טסט ספציפי
```bash
python tests/run_tests.py command    # רק טסטי Command
python tests/run_tests.py game       # רק טסטי Game
python tests/run_tests.py physics    # רק טסטי Physics
```

### הרצה ישירה של קובץ טסט
```bash
python tests/test_command.py
python tests/test_game.py
```

## 🧪 תיאור הטסטים

### test_command.py
- **מה נבדק**: מחלקת Command ושיטות היצירה שלה
- **מוקים**: אין (מחלקה פשוטה ללא תלות)
- **טסטים עיקריים**:
  - יצירת פקודות מכל הסוגים
  - ולידציה של פרמטרים
  - מקרי קיצון

### test_game.py  
- **מה נבדק**: לולאת המשחק הראשית
- **מוקים**: pygame, ThreadedInputManager, StatisticsManager
- **טסטים עיקריים**:
  - אתחול המשחק
  - זיהוי התנגשויות
  - תנאי ניצחון
  - ציור ועדכון

### test_threaded_input_manager.py
- **מה נבדק**: מערכת הקלט המשורשרת
- **מוקים**: threading, keyboard input
- **טסטים עיקריים**:
  - הפעלה ועצירה של threads
  - עיבוד קלט
  - thread safety

### test_physics.py
- **מה נבדק**: מערכת הפיזיקה והתנועה
- **מוקים**: Command
- **טסטים עיקריים**:
  - חישובי תנועה
  - מהירויות שונות
  - תנועה אלכסונית
  - השלמת תנועה

### test_graphics.py
- **מה נבדק**: מערכת הגרפיקה
- **מוקים**: IMG (מוק לmychete IMG)
- **טסטים עיקריים**:
  - מעברי מצבים
  - ציור
  - העתקה
  - מצבים שונים

### test_state.py
- **מה נבדק**: מכונת המצבים
- **מוקים**: Graphics, Physics
- **טסטים עיקריים**:
  - מעברי מצבים
  - התחלת פקודות
  - עדכון מצב
  - העתקה

### test_board.py
- **מה נבדק**: הלוח והכלים עליו
- **מוקים**: PieceFactory, State
- **טסטים עיקריים**:
  - טעינה מCSV
  - הוספה/הסרה של כלים
  - ולידציה של מיקומים
  - העתקת לוח

### test_piece.py
- **מה נבדק**: מחלקת הכלי הבודד
- **מוקים**: State, Moves
- **טסטים עיקריים**:
  - זיהוי צבע וסוג
  - מהלכים אפשריים
  - התחלת פקודות
  - העתקה

### test_mock_img.py
- **מה נבדק**: מחלקת MockImg
- **מוקים**: numpy
- **טסטים עיקריים**:
  - טעינת תמונות
  - מטמון תמונות
  - ציור
  - יעילות זיכרון

## 🎯 עקרונות הטסטים

### 1. שימוש במוקים
- **למה**: מניעת תלות ברכיבים חיצוניים (pygame, numpy, קבצים)
- **איך**: `unittest.mock.Mock` ו-`@patch` decorators
- **יתרון**: טסטים מהירים ויציבים

### 2. בידוד טסטים
- כל טסט עצמאי ולא תלוי באחרים
- `setUp()` מכין נתונים נקיים לכל טסט
- מוקים מאופסים בין טסטים

### 3. כיסוי מקרי קיצון
- ערכי קלט לא תקינים
- מיקומים מחוץ ללוח
- פקודות לא צפויות
- מצבי שגיאה

### 4. בדיקת התנהגות
- לא רק תוצאות אלא גם אופן הפעולה
- בדיקה שפונקציות נקראו עם הפרמטרים הנכונים
- בדיקת מספר קריאות

## 📊 סטטיסטיקות

- **9 קבצי טסט** מקיפים
- **~150 טסטים** בסך הכל  
- **כיסוי מלא** של המחלקות הראשיות
- **מוקים מקצועיים** לכל התלות החיצוניות

## 🔧 הוספת טסטים חדשים

### תבנית לטסט חדש:
```python
#!/usr/bin/env python3
"""
🧪 טסטים מקיפים למחלקת [CLASS_NAME]
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Test[ClassName](unittest.TestCase):
    """טסטים מקיפים למחלקת [CLASS_NAME]"""
    
    def setUp(self):
        """הכנת נתונים לכל טסט"""
        pass
    
    def test_[functionality](self):
        """🧪 טסט [description]"""
        # Arrange
        # Act  
        # Assert
        pass

if __name__ == '__main__':
    print("🧪 הרצת טסטים למחלקת [CLASS_NAME]...")
    unittest.main(verbosity=2)
```

## 🚀 המלצות

1. **הריצו טסטים לפני כל commit**
2. **הוסיפו טסטים לפונקציונליות חדשה**
3. **השתמשו במוקים בחכמה** - אל תמקו יותר מדי
4. **כתבו טסטים קריאים** עם שמות ותיאורים ברורים

---

**מערכת הטסטים הזו מבטיחה איכות ויציבות של הקוד! 🧪✨**
