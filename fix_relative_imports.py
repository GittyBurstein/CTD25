#!/usr/bin/env python3
"""
Script to fix all relative import statements in the reorganized chess project
"""

import os
import re
from pathlib import Path

def fix_relative_imports_in_file(file_path):
    """Fix relative imports in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace relative imports with absolute imports
    # Pattern: from .MODULE import CLASS
    content = re.sub(r'from \.(\w+) import', r'from \1 import', content)
    
    # Pattern: from . import MODULE
    content = re.sub(r'from \. import (\w+)', r'import \1', content)
    
    # Write back the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed relative imports in {file_path}")

def main():
    """Main function to fix all relative imports"""
    base_path = Path(__file__).parent
    
    # Directories to process
    dirs_to_process = [
        base_path / "client" / "interfaces",
        base_path / "server" / "interfaces",
        base_path / "shared" / "interfaces",
        base_path / "client",
        base_path / "server"
    ]
    
    for directory in dirs_to_process:
        if directory.exists():
            print(f"Processing directory: {directory}")
            for py_file in directory.glob("**/*.py"):
                if py_file.name != "__pycache__":
                    fix_relative_imports_in_file(py_file)
    
    print("Relative import fixing completed!")

if __name__ == "__main__":
    main()
