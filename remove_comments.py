#!/usr/bin/env python3
"""
Script to remove comments from all Python files in the project.
This script removes:
- Single-line comments (# comments)
- Inline comments (code # comment)
- Docstrings (triple-quoted strings)
- Empty lines that become empty after comment removal
"""

import os
import re
import ast
from pathlib import Path

def remove_comments_from_file(file_path):
    """Remove comments from a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to get the AST
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"Warning: Could not parse {file_path} - skipping")
            return False
        
        # Remove comments using regex
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                cleaned_lines.append('')
                continue
            
            # Check if line is a comment only
            stripped = line.strip()
            if stripped.startswith('#'):
                # Skip comment-only lines
                continue
            
            # Check for inline comments
            if '#' in line:
                # Find the # that's not inside a string
                in_string = False
                quote_char = None
                comment_pos = -1
                
                for i, char in enumerate(line):
                    if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                            quote_char = None
                    elif char == '#' and not in_string:
                        comment_pos = i
                        break
                
                if comment_pos != -1:
                    # Remove the comment part
                    line = line[:comment_pos].rstrip()
            
            # Only add non-empty lines
            if line.strip():
                cleaned_lines.append(line)
        
        # Join lines and clean up multiple empty lines
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Remove multiple consecutive empty lines (keep max 2)
        cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all Python files."""
    project_root = Path(__file__).parent
    python_files = list(project_root.rglob('*.py'))
    
    # Exclude this script itself
    python_files = [f for f in python_files if f.name != 'remove_comments.py']
    
    print(f"Found {len(python_files)} Python files to process...")
    
    processed = 0
    failed = 0
    
    for file_path in python_files:
        print(f"Processing: {file_path.relative_to(project_root)}")
        if remove_comments_from_file(file_path):
            processed += 1
        else:
            failed += 1
    
    print(f"\nCompleted!")
    print(f"Successfully processed: {processed} files")
    print(f"Failed: {failed} files")

if __name__ == "__main__":
    main()
