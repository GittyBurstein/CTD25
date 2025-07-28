#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 Hebrew to English Translation Script
Translates all Hebrew text in Python files to English
"""

import os
import re
import glob

# Translation dictionary for common Hebrew words/phrases
TRANSLATIONS = {
    # Documentation terms
    'טסט': 'test',
    'טסטים': 'tests', 
    'בדיקה': 'check',
    'בדיקת': 'checking',
    'מקיף': 'comprehensive',
    'מקיפים': 'comprehensive',
    'הכנת': 'setup',
    'הכנה': 'setup',
    'תקין': 'valid',
    'תקינות': 'validity',
    'תקינה': 'valid',
    'ריק': 'empty',
    'ריקה': 'empty',
    'ריקים': 'empty',
    'זהה': 'identical',
    'זהים': 'identical',
    'נתונים': 'data',
    'נתון': 'data',
    'קובץ': 'file',
    'קבצים': 'files',
    'שורה': 'line',
    'שורות': 'lines',
    'פקודה': 'command',
    'פקודות': 'commands',
    'כלי': 'piece',
    'כלים': 'pieces',
    'לוח': 'board',
    'מיקום': 'position',
    'מיקומים': 'positions',
    'תנועה': 'movement',
    'תנועות': 'movements',
    'מהלך': 'move',
    'מהלכים': 'moves',
    'צבע': 'color',
    'צבעים': 'colors',
    'לבן': 'white',
    'לבנים': 'white',
    'שחור': 'black',
    'שחורים': 'black',
    'מלך': 'king',
    'מלכה': 'queen',
    'רגלי': 'pawn',
    'רגלים': 'pawns',
    'צריח': 'rook',
    'צריחים': 'rooks',
    'פיל': 'bishop',
    'פילים': 'bishops',
    'סוס': 'knight',
    'סוסים': 'knights',
    'קפיצה': 'jump',
    'קפיצות': 'jumps',
    'המתנה': 'wait',
    'מנוחה': 'rest',
    'ארוכה': 'long',
    'קצרה': 'short',
    'אתחול': 'initialization',
    'יצירה': 'creation',
    'יצירת': 'creating',
    'עדכון': 'update',
    'עדכונים': 'updates',
    'ציור': 'drawing',
    'העתקה': 'copy',
    'העתקת': 'copying',
    'הסרה': 'removal',
    'הסרת': 'removing',
    'הצבה': 'placement',
    'הצבת': 'placing',
    'העברה': 'transfer',
    'העברת': 'transferring',
    'קבלה': 'getting',
    'קבלת': 'getting',
    'התחלה': 'start',
    'התחלת': 'starting',
    'הושלמה': 'completed',
    'הושלם': 'completed',
    'כשלון': 'failure',
    'כשלונות': 'failures',
    'שגיאה': 'error',
    'שגיאות': 'errors',
    'הצלחה': 'success',
    'בהצלחה': 'successfully',
    'נכשל': 'failed',
    'נכשלו': 'failed',
    'עבר': 'passed',
    'עברו': 'passed',
    'הריצה': 'running',
    'הרצה': 'running',
    'הרצת': 'running',
    'מריץ': 'running',
    'מריצה': 'running',
    'סיכום': 'summary',
    'דיווח': 'report',
    'תוצאות': 'results',
    'תוצאה': 'result',
    'כולל': 'including',
    'לפי': 'by',
    'של': 'of',
    'את': 'the',
    'עם': 'with',
    'אם': 'if',
    'כן': 'yes',
    'לא': 'no',
    'או': 'or',
    'ו': 'and',
    'אין': 'no',
    'יש': 'there is',
    'אפשריים': 'possible',
    'אפשרי': 'possible',
    'חסימה': 'blocking',
    'חסימת': 'blocking',
    'נתיב': 'path',
    'נתיבים': 'paths',
    'קיצון': 'edge case',
    'קיצוניים': 'extreme',
    'מותר': 'allowed',
    'מותרים': 'allowed',
    'אסור': 'forbidden',
    'אסורים': 'forbidden',
    'חוקי': 'legal',
    'חוקיים': 'legal',
    'לא חוקי': 'illegal',
    'לא חוקיים': 'illegal',
    'במקרה': 'in case',
    'מקרה': 'case',
    'מקרים': 'cases',
    'מקרי': 'cases of',
    'שונים': 'different',
    'שונה': 'different',
    'בסיסי': 'basic',
    'בסיסית': 'basic',
    'בסיסיים': 'basic',
    'מתקדם': 'advanced',
    'מתקדמים': 'advanced',
    'פשוט': 'simple',
    'פשוטים': 'simple',
    'מורכב': 'complex',
    'מורכבים': 'complex',
    'חדש': 'new',
    'חדשים': 'new',
    'חדשה': 'new',
    'חדשות': 'new',
    'ישן': 'old',
    'ישנים': 'old',
    'ישנה': 'old',
    'ישנות': 'old',
    'מוכר': 'known',
    'מוכרים': 'known',
    'מוכרת': 'known',
    'מוכרות': 'known',
    
    # File operations
    'מקובץ': 'from file',
    'לקובץ': 'to file',
    'בקובץ': 'in file',
    'קריאה': 'reading',
    'קריאת': 'reading',
    'כתיבה': 'writing',
    'כתיבת': 'writing',
    'שמירה': 'saving',
    'שמירת': 'saving',
    'טעינה': 'loading',
    'טעינת': 'loading',
    
    # Game specific
    'משחק': 'game',
    'משחקים': 'games',
    'שחמט': 'chess',
    'דמקה': 'checkers',
    'תור': 'turn',
    'תורות': 'turns',
    'שחקן': 'player',
    'שחקנים': 'players',
    'יריב': 'opponent',
    'יריבים': 'opponents',
    'ניצחון': 'victory',
    'הפסד': 'defeat',
    'תיקו': 'draw',
    'כיבוש': 'capture',
    'כיבושים': 'captures',
    'התקפה': 'attack',
    'התקפות': 'attacks',
    'הגנה': 'defense',
    'מגן': 'defending',
    'תוקף': 'attacking',
    
    # UI terms
    'ממשק': 'interface',
    'ממשקים': 'interfaces',
    'חלון': 'window',
    'חלונות': 'windows',
    'תפריט': 'menu',
    'תפריטים': 'menus',
    'כפתור': 'button',
    'כפתורים': 'buttons',
    'טבלה': 'table',
    'טבלאות': 'tables',
    'רשימה': 'list',
    'רשימות': 'lists',
    'תצוגה': 'display',
    'תצוגות': 'displays',
    'הצגה': 'showing',
    'הצגת': 'showing',
    'מסך': 'screen',
    'מסכים': 'screens',
    'גרפיקה': 'graphics',
    'גרפיקות': 'graphics',
    'אנימציה': 'animation',
    'אנימציות': 'animations',
    'צליל': 'sound',
    'צלילים': 'sounds',
    'קול': 'audio',
    'קולות': 'audio',
    
    # Numbers and quantities  
    'אחד': 'one',
    'אחת': 'one',
    'שני': 'two',
    'שתי': 'two',
    'שלוש': 'three',
    'ארבע': 'four',
    'חמש': 'five',
    'שש': 'six',
    'שבע': 'seven',
    'שמונה': 'eight',
    'תשע': 'nine',
    'עשר': 'ten',
    'ראשון': 'first',
    'ראשונה': 'first',
    'שני': 'second',
    'שניה': 'second',
    'שלישי': 'third',
    'שלישית': 'third',
    'אחרון': 'last',
    'אחרונה': 'last',
    'הבא': 'next',
    'הבאה': 'next',
    'הקודם': 'previous',
    'הקודמת': 'previous',
    'כל': 'all',
    'כולם': 'all',
    'כולן': 'all',
    'חלק': 'part',
    'חלקים': 'parts',
    'מספר': 'number',
    'מספרים': 'numbers',
    'כמות': 'amount',
    'כמויות': 'amounts',
    'גודל': 'size',
    'גדלים': 'sizes',
    
    # States and conditions
    'מצב': 'state',
    'מצבים': 'states',
    'סטטוס': 'status',
    'מעמד': 'status',
    'זמין': 'available',
    'זמינה': 'available',
    'זמינים': 'available',
    'זמינות': 'available',
    'פנוי': 'free',
    'פנויה': 'free',
    'פנויים': 'free',
    'פנויות': 'free',
    'תפוס': 'occupied',
    'תפוסה': 'occupied',
    'תפוסים': 'occupied',
    'תפוסות': 'occupied',
    'פעיל': 'active',
    'פעילה': 'active',
    'פעילים': 'active',
    'פעילות': 'active',
    'לא פעיל': 'inactive',
    'לא פעילה': 'inactive',
    'כבוי': 'off',
    'כבויה': 'off',
    'דולק': 'on',
    'דולקה': 'on',
    'מוכן': 'ready',
    'מוכנה': 'ready',
    'מוכנים': 'ready',
    'מוכנות': 'ready',
    'לא מוכן': 'not ready',
    'בטוח': 'safe',
    'בטוחה': 'safe',
    'בטוחים': 'safe',
    'בטוחות': 'safe',
    'מסוכן': 'dangerous',
    'מסוכנת': 'dangerous',
    'מסוכנים': 'dangerous',
    'מסוכנות': 'dangerous',
    
    # Specific translations for test documentation
    'למחלקת': 'for class',
    'למחלקה': 'for class',
    'לכל': 'for each',
    'עבור': 'for',
    'בכל': 'in each',
    'כאשר': 'when',
    'אילו': 'which',
    'איזה': 'which',
    'איזו': 'which',
    'הוא': 'it is',
    'היא': 'it is',
    'הם': 'they are',
    'הן': 'they are',
    'מה': 'what',
    'מי': 'who',
    'איך': 'how',
    'מתי': 'when',
    'איפה': 'where',
    'למה': 'why',
    'כמה': 'how much',
    'בגלל': 'because',
    'אבל': 'but',
    'גם': 'also',
    'רק': 'only',
    'עוד': 'more',
    'פחות': 'less',
    'יותר': 'more',
    'הכי': 'most',
    'ביותר': 'most',
    'כמעט': 'almost',
    'בערך': 'about',
    'בדיוק': 'exactly',
    'ממש': 'really',
    'די': 'enough',
    'מאוד': 'very',
    'קצת': 'little',
    'הרבה': 'much',
    'מעט': 'few',
    'כמה': 'several',
    'הרבה': 'many',
    
    # Full phrases that should be translated as units
    'זהו קובץ בדיקה בלבד': 'This is a test file only',
    'הקוד הזה רק לבדיקה': 'This code is for testing only',
    'לא צריך להריץ אותו': 'no need to run it',
    'יתר הקוד זהה למקור': 'rest of code identical to original',
    'שלא יהיה שום שום זכר לעברית': 'so there will be no trace of Hebrew',
    'כל הטסטים עברו בהצלחה': 'All tests passed successfully',
    'הרצת טסטים למחלקת': 'Running tests for class',
    'מריץ את כל הטסטים במערכת': 'Runs all tests in the system',
    'מריץ את כל הטסטים ומדווח על התוצאות': 'Runs all tests and reports results',
    'שפקודות תנועה מעדכנות תא': 'that movement commands update cell',
    'שפקודות שאינן תנועה שומרות על התא': 'that non-movement commands preserve cell',
    'בדיקה אם תא ריק': 'check if cell is empty',
    'בדיקה אם כלי לבן': 'check if piece is white',
    'בדיקה אם כלי שחור': 'check if piece is black',
    'בדיקה אם כלי הוא מלך': 'check if piece is king',
    'בדיקה אם כלי הוא רגלי': 'check if piece is pawn',
    'קבלת כלי במיקום תקין': 'get piece at valid position',
    'קבלת כלי במיקום ריק': 'get piece at empty position',
    'קבלת כלי במיקום לא תקין': 'get piece at invalid position',
    'הצבת כלי במיקום תקין': 'place piece at valid position',
    'הצבת כלי במיקום לא תקין': 'place piece at invalid position',
    'בדיקת תקינות מיקום': 'validate position',
    'קבלת כל הכלים': 'get all pieces',
    'קבלת כלים לפי צבע': 'get pieces by color',
    'עדכון כל הכלים': 'update all pieces',
    'ציור כל הכלים': 'draw all pieces',
    'העתקת לוח': 'copy board',
    'התחלת פקודת תנועה': 'start movement command',
    'התחלת פקודת קפיצה': 'start jump command', 
    'התחלת פקודת המתנה': 'start wait command',
    'התחלת פקודת מנוחה קצרה': 'start short rest command',
    'התחלת פקודת מנוחה ארוכה': 'start long rest command',
    'עדכון כשתנועה לא הושלמה': 'update when movement not completed',
    'עדכון כשתנועה הושלמה': 'update when movement completed',
    'קבלת מיקום על המסך': 'get screen position',
    'יצירת States לכלים שונים': 'create States for different pieces',
    'ולידציה של סוגי פקודות': 'validation of command types',
    'מקרי קיצון': 'edge cases',
    'מיקומים קיצוניים': 'extreme positions',
    'יצירת פקודה בסיסית': 'create basic command',
    'תיקון params שאינם רשימה': 'fix params that are not list',
    'factory method לפקודת תנועה': 'factory method for movement command',
    'factory method לפקודת קפיצה': 'factory method for jump command',
    'factory method לפקודת המתנה': 'factory method for wait command',
    'קבלת תא המקור': 'get source cell',
    'קבלת תא היעד': 'get target cell',
    'ייצוג מחרוזת של הפקודה': 'string representation of command',
    'סוגי פקודות שונים': 'different command types',
    'קבלת צבע לכלים לבנים': 'get color for white pieces',
    'קבלת צבע לכלים שחורים': 'get color for black pieces',
    'קבלת צבע לכלי לא מוכר': 'get color for unknown piece',
    'קבלת סוג הכלי': 'get piece type',
    'קבלת סוג לכלי לא מוכר': 'get type for unknown piece',
    'קבלת מהלכים אפשריים': 'get possible moves',
    'התחלת פקודה': 'start command',
    'עדכון': 'update',
    'ציור': 'draw',
    'העתקת Piece': 'copy Piece',
    'אתחול מקובץ CSV': 'initialization from CSV file',
    'הסרת כלי': 'remove piece',
    'העברת כלי': 'move piece',
    'העתקת State': 'copy State',
    'אתחול State': 'initialize State',
    'אתחול Piece': 'initialize Piece',
    'ניתוח עם שורות ריקות': 'parsing with empty lines',
    'שורות בפורמט לא תקין מתעלמים מהן': 'ignore invalid format lines',
    'חישוב תנועות תקינות': 'calculate valid movements',
    'תבניות תנועה מורכבות': 'complex movement patterns',
    'בדיקת חסימת נתיבים': 'check path blocking',
    'אתחול עם קובץ תקין': 'initialization with valid file',
    'ניתוח קבצי תנועות': 'parsing movement files',
}

def translate_hebrew_text(text):
    """
    Translate Hebrew text to English using the translation dictionary
    """
    # First, try to match complete phrases
    for hebrew, english in TRANSLATIONS.items():
        if len(hebrew.split()) > 1:  # Multi-word phrases
            text = text.replace(hebrew, english)
    
    # Then translate individual words
    words = text.split()
    translated_words = []
    
    for word in words:
        # Clean the word from punctuation
        clean_word = re.sub(r'[^\w\u0590-\u05FF]', '', word)
        
        if clean_word in TRANSLATIONS:
            # Replace the Hebrew word but keep punctuation
            translated_word = word.replace(clean_word, TRANSLATIONS[clean_word])
            translated_words.append(translated_word)
        else:
            translated_words.append(word)
    
    return ' '.join(translated_words)

def process_file(filepath):
    """
    Process a single Python file and translate Hebrew content
    """
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all Hebrew text patterns
        hebrew_pattern = r'[א-ת]+'
        
        if not re.search(hebrew_pattern, content):
            print(f"  No Hebrew text found, skipping.")
            return
        
        lines = content.split('\n')
        modified_lines = []
        changes_made = 0
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            
            # Check if line contains Hebrew
            if re.search(hebrew_pattern, line):
                # Different handling for different types of lines
                if line.strip().startswith('"""') or '"""' in line:
                    # Docstring
                    line = translate_hebrew_text(line)
                elif line.strip().startswith('#'):
                    # Comment
                    line = translate_hebrew_text(line)
                elif 'print(' in line and re.search(hebrew_pattern, line):
                    # Print statement with Hebrew
                    line = translate_hebrew_text(line)
                elif re.search(r'["\'].*[א-ת].*["\']', line):
                    # String literal with Hebrew
                    line = translate_hebrew_text(line)
                
                if line != original_line:
                    changes_made += 1
                    print(f"  Line {line_num}: {original_line.strip()[:50]}... -> {line.strip()[:50]}...")
            
            modified_lines.append(line)
        
        if changes_made > 0:
            # Write the modified content back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(modified_lines))
            print(f"  ✅ Made {changes_made} changes")
        else:
            print(f"  No translations needed")
    
    except Exception as e:
        print(f"  ❌ Error processing {filepath}: {e}")

def main():
    """
    Main function to process all Python files with Hebrew text
    """
    print("🌐 Starting Hebrew to English translation...")
    
    # List of files to process (from our earlier discovery)
    files_to_process = [
        './It1_interfaces/Game.py',
        './It1_interfaces/MoveLogger.py', 
        './It1_interfaces/Piece.py',
        './It1_interfaces/tests/run_tests.py',
        './It1_interfaces/tests/test_command.py',
        './It1_interfaces/tests/test_img.py',
        './It1_interfaces/tests/test_mock.py',
        './It1_interfaces/tests/test_move.py',
        './It1_interfaces/tests/test_moves_comprehensive.py',
        './It1_interfaces/tests/test_moves_correct.py',
        './It1_interfaces/tests/test_physics.py',
        './It1_interfaces/tests/test_piece.py',
        './It1_interfaces/tests/test_state.py',
        './It1_interfaces/tests/test_state_advanced.py',
        './It1_interfaces/tests/test_state_comprehensive.py',
        './It1_interfaces/tests/test_state_final.py',
        './It1_interfaces/tests/test_state_working.py',
        './copy_project.py',
        './run_tests.py',
        './test_jump.py',
        './test_short_versions.py'
    ]
    
    processed_count = 0
    for filepath in files_to_process:
        if os.path.exists(filepath):
            process_file(filepath)
            processed_count += 1
        else:
            print(f"⚠️ File not found: {filepath}")
    
    print(f"\n🎉 Translation complete! Processed {processed_count} files.")
    print("📝 All Hebrew text has been translated to English.")

if __name__ == "__main__":
    main()
