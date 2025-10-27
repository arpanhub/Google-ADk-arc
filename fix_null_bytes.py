#!/usr/bin/env python3
"""Fix null bytes in Python source files"""

from pathlib import Path

def fix_file(file_path):
    """Check and fix null bytes in a file"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    # Read as bytes first
    content_bytes = path.read_bytes()
    null_count = content_bytes.count(b'\x00')
    
    print(f"📁 {file_path}")
    print(f"   Size: {len(content_bytes)} bytes, Null bytes: {null_count}")
    
    if null_count == 0:
        print("   ✅ No null bytes found")
        return True
    
    # Try to decode and fix
    try:
        # Try UTF-16 first (common cause of null bytes)
        if content_bytes.startswith((b'\xff\xfe', b'\xfe\xff')):
            content_str = content_bytes.decode('utf-16')
            print("   🔧 Decoded as UTF-16")
        else:
            # Try UTF-16 without BOM
            try:
                content_str = content_bytes.decode('utf-16le')
                print("   🔧 Decoded as UTF-16LE")
            except:
                # Remove null bytes manually
                content_str = content_bytes.replace(b'\x00', b'').decode('utf-8', errors='ignore')
                print("   🔧 Removed null bytes manually")
        
        # Write back as UTF-8
        path.write_text(content_str, encoding='utf-8')
        print("   ✅ Fixed and saved as UTF-8")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to fix: {e}")
        return False

def main():
    files_to_check = [
        r"d:\Propel\ADK\getting_started\multi_tool_agent\agent.py",
        r"d:\Propel\ADK\getting_started\multi_tool_agent\__init__.py"
    ]
    
    print("🔍 Checking for null bytes in Python files...\n")
    
    all_good = True
    for file_path in files_to_check:
        if not fix_file(file_path):
            all_good = False
        print()
    
    if all_good:
        print("🎉 All files are clean!")
    else:
        print("⚠️  Some files had issues")

if __name__ == "__main__":
    main()