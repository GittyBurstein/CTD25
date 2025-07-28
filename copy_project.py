import shutil
import os
import sys

def copy_project_to_english_path():
"""מעתיק the הפרויקט לתיקייה with שם באנגלית בלבד"""
    
# path נוכחי
    current_path = os.getcwd()
print(f"נתיב נוכחי: {current_path}")
    
# יוצר path new באנגלית בלבד
# עולה רמה one למעלה ויוצר תיקייה new
    parent_dir = os.path.dirname(current_path)
    new_project_path = os.path.join(parent_dir, "chess_project_english")
    
print(f"נתיב new: {new_project_path}")
    
    try:
# if התיקייה קיימת, מוחק אותה
        if os.path.exists(new_project_path):
print("מוחק תיקייה קיימת...")
            shutil.rmtree(new_project_path)
        
# מעתיק the all התיקייה
print("מעתיק files...")
        shutil.copytree(current_path, new_project_path)
        
print(f"✅ הפרויקט הועתק successfully!")
print(f"📁 הנתיב החדש: {new_project_path}")
print("\n🔧 כדי להמשיך לעבוד:")
print("1. פתח terminal/cmd new")
print(f"2. הכנס לתיקייה: cd \"{new_project_path}\"")
print("3. הרץ: python main.py")
        
        return new_project_path
        
    except Exception as e:
print(f"❌ error בהעתקה: {e}")
        return None

def create_simple_run_script():
"""יוצר file running simple"""
    script_content = """@echo off
echo Starting Kung Fu Chess...
cd /d "%~dp0"
python main.py
pause
"""
    
    with open("run_game.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
print("✅ נוצר file run_game.bat - תוכל להקליק עליו כדי להריץ the המשחק")

if __name__ == "__main__":
print("🥋 מעתיק פרויקט Kung Fu Chess לנתיב באנגלית...")
    print("=" * 50)
    
    new_path = copy_project_to_english_path()
    
    if new_path:
# יוצר file bat להרצה קלה
        current_dir = os.getcwd()
        os.chdir(new_path)
        create_simple_run_script()
        os.chdir(current_dir)
        
        print("\n" + "=" * 50)
print("🎯 ההעתקה completed!")
print("כעת for לתיקייה החדשה והרץ the המשחק")
