#!/usr/bin/env python3
"""
Script to fix duplicate summary sections in transcript files.
"""

import os
import re
from pathlib import Path
from datetime import datetime

# Set working directory to the script's location
os.chdir(Path(__file__).parent)

def is_duplicate_summary(line1, line2):
    """Check if two lines are duplicate summary headers."""
    # Both must start with ##
    if not (line1.startswith('## ') and line2.startswith('## ')):
        return False
    
    # Both must contain "Summary" and have a link
    if not ('Summary' in line1 and 'Summary' in line2 and '(' in line1 and '(' in line2):
        return False
    
    # Extract dates from both lines using multiple patterns
    date_patterns = [
        r'(\d{1,2}\s+\w+\s+\d{4})',  # "29 March 2025"
        r'(\w+\s+\d{1,2}(?:st|nd|rd|th)?,\s+\d{4})',  # "March 29, 2025" or "March 29th, 2025"
    ]
    
    date1, date2 = None, None
    
    for pattern in date_patterns:
        if not date1:
            match = re.search(pattern, line1)
            if match:
                date1 = match.group(1)
        if not date2:
            match = re.search(pattern, line2)
            if match:
                date2 = match.group(1)
    
    if date1 and date2:
        # Simple string comparison if they're exactly the same
        if date1 == date2:
            return True
        
        # Try to parse different formats and compare
        try:
            formats = ['%d %B %Y', '%B %d, %Y', '%B %dst, %Y', '%B %dnd, %Y', '%B %drd, %Y', '%B %dth, %Y']
            parsed1, parsed2 = None, None
            
            for fmt in formats:
                try:
                    if not parsed1:
                        parsed1 = datetime.strptime(date1, fmt)
                except:
                    pass
                try:
                    if not parsed2:
                        parsed2 = datetime.strptime(date2, fmt)
                except:
                    pass
            
            if parsed1 and parsed2:
                return parsed1.date() == parsed2.date()
                
        except:
            pass
    
    return False

def fix_duplicate_summaries(file_path):
    """Fix duplicate summary sections in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Find all summary sections
        summary_indices = []
        for i, line in enumerate(lines):
            if line.startswith('## ') and 'Summary' in line and '(' in line:
                summary_indices.append(i)
        
        if len(summary_indices) <= 1:
            return False  # No duplicates
        
        # Check for duplicates and remove them
        lines_to_remove = set()
        
        for i in range(len(summary_indices)):
            for j in range(i + 1, len(summary_indices)):
                idx1, idx2 = summary_indices[i], summary_indices[j]
                if is_duplicate_summary(lines[idx1], lines[idx2]):
                    print(f"   🗑️  Removing duplicate summary at line {idx2 + 1}")
                    
                    # Mark the second occurrence and its content for removal
                    # Find the end of this section (next ## or end of file)
                    section_end = len(lines)
                    for k in range(idx2 + 1, len(lines)):
                        if lines[k].startswith('## '):
                            section_end = k
                            break
                    
                    # Mark all lines in this duplicate section for removal
                    for k in range(idx2, section_end):
                        lines_to_remove.add(k)
                    
                    # Also remove any preceding separator lines
                    for k in range(idx2 - 1, -1, -1):
                        if lines[k].strip() == '---' or lines[k].strip() == '':
                            lines_to_remove.add(k)
                        else:
                            break
        
        if lines_to_remove:
            # Remove marked lines
            new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
            new_content = '\n'.join(new_lines)
            
            # Write back to file
            file_path.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"   ❌ Error processing {file_path.name}: {e}")
        return False

def main():
    """Main function to fix all duplicate summaries."""
    transcript_folder = Path("transcripts")
    
    if not transcript_folder.exists():
        print("❌ Transcripts folder not found!")
        return
    
    print("DUPLICATE SUMMARY FIXER")
    print("=" * 50)
    print("Fixing duplicate summary sections...\n")
    
    fixed_count = 0
    total_count = 0
    
    for file_path in transcript_folder.glob("*.md"):
        total_count += 1
        print(f"📄 Processing: {file_path.name}")
        
        if fix_duplicate_summaries(file_path):
            print(f"   ✅ Fixed duplicates")
            fixed_count += 1
        else:
            print(f"   ✅ No duplicates found")
    
    print(f"\n" + "=" * 50)
    print(f"📊 Summary: Fixed {fixed_count} out of {total_count} files")
    
    if fixed_count > 0:
        print(f"🎉 Successfully removed duplicate summaries from {fixed_count} file(s)!")
    else:
        print("✅ No duplicate summaries found!")

if __name__ == "__main__":
    main()