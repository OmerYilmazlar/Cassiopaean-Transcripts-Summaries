import os
import re
from pathlib import Path
from difflib import SequenceMatcher

# Set working directory to the script's location
os.chdir(Path(__file__).parent)

def extract_sections(content):
    """Extract all sections with their content."""
    sections = {}
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if line.startswith('## '):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line[3:].strip()
            current_content = [line]
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def count_bullets_in_text(text):
    """Count bullet points in a text block."""
    return len([line for line in text.split('\n') if line.strip().startswith('- ')])

def extract_bullets_from_text(text):
    """Extract all bullet points from a text block."""
    bullets = []
    for line in text.split('\n'):
        if line.strip().startswith('- '):
            bullets.append(line.strip())
    return bullets

def is_duplicate_section(section_name1, section_name2):
    """Check if two sections are duplicates (especially summary sections)."""
    # Normalize section names for comparison
    name1 = section_name1.lower().strip()
    name2 = section_name2.lower().strip()
    
    # Check for summary duplicates with different formats
    if 'summary' in name1 and 'summary' in name2:
        # Extract dates from both section names
        import re
        date_pattern = r'(\d{1,2}\s+\w+\s+\d{4})'
        date1 = re.search(date_pattern, name1)
        date2 = re.search(date_pattern, name2)
        
        if date1 and date2:
            # If dates are the same, it's a duplicate
            return date1.group(1) == date2.group(1)
    
    return False

def merge_section_content(current_section, original_section):
    """Merge content from original into current, preserving structure."""
    current_bullets = extract_bullets_from_text(current_section)
    original_bullets = extract_bullets_from_text(original_section)
    
    # If current has fewer bullets than original, we need to restore missing ones
    if len(current_bullets) < len(original_bullets):
        # Find which bullets are missing
        missing_bullets = []
        
        for orig_bullet in original_bullets:
            # Check if this bullet (or similar) exists in current
            found = False
            for curr_bullet in current_bullets:
                # Use similarity matching to account for minor formatting differences
                similarity = SequenceMatcher(None, orig_bullet.lower(), curr_bullet.lower()).ratio()
                if similarity > 0.8:  # 80% similarity threshold
                    found = True
                    break
            
            if not found:
                missing_bullets.append(orig_bullet)
        
        if missing_bullets:
            # Rebuild the section with missing bullets added
            lines = current_section.split('\n')
            new_lines = []
            
            for line in lines:
                new_lines.append(line)
                # If this is the section header, add missing bullets after existing ones
                if line.startswith('## '):
                    continue
            
            # Find where to insert missing bullets (after existing bullets)
            insert_index = len(new_lines)
            for i in range(len(new_lines) - 1, -1, -1):
                if new_lines[i].strip().startswith('- '):
                    insert_index = i + 1
                    break
                elif new_lines[i].startswith('## '):
                    # Find first bullet after header
                    for j in range(i + 1, len(new_lines)):
                        if new_lines[j].strip().startswith('- '):
                            continue
                        elif new_lines[j].strip() == '':
                            continue
                        else:
                            insert_index = j
                            break
                    break
            
            # Insert missing bullets
            for bullet in missing_bullets:
                new_lines.insert(insert_index, bullet)
                insert_index += 1
            
            return '\n'.join(new_lines)
    
    return current_section

def compare_and_fix_transcript(filename):
    """Compare current transcript with original and fix missing content."""
    current_path = Path("transcripts") / filename
    original_path = Path("originals") / filename
    
    if not current_path.exists():
        print(f"❌ Current file not found: {filename}")
        return False
    
    if not original_path.exists():
        print(f"⚠️  Original file not found: {filename}")
        return False
    
    try:
        current_content = current_path.read_text(encoding='utf-8')
        original_content = original_path.read_text(encoding='utf-8')
        
        current_sections = extract_sections(current_content)
        original_sections = extract_sections(original_content)
        
        changes_made = False
        fixed_sections = {}
        
        # Compare each section
        for section_name in current_sections.keys():
            if section_name in original_sections:
                current_bullets = count_bullets_in_text(current_sections[section_name])
                original_bullets = count_bullets_in_text(original_sections[section_name])
                
                if current_bullets < original_bullets:
                    print(f"   🔧 Fixing '{section_name}': {current_bullets} → {original_bullets} bullets")
                    fixed_sections[section_name] = merge_section_content(
                        current_sections[section_name], 
                        original_sections[section_name]
                    )
                    changes_made = True
                else:
                    fixed_sections[section_name] = current_sections[section_name]
            else:
                fixed_sections[section_name] = current_sections[section_name]
        
        # Check for completely missing sections
        for section_name in original_sections.keys():
            if section_name not in current_sections:
                # Check if this is a duplicate of an existing section
                is_duplicate = False
                for existing_section in current_sections.keys():
                    if is_duplicate_section(section_name, existing_section):
                        print(f"   ⚠️  Skipping duplicate section: '{section_name}' (similar to '{existing_section}')")
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    print(f"   ➕ Adding missing section: '{section_name}'")
                    fixed_sections[section_name] = original_sections[section_name]
                    changes_made = True
        
        if changes_made:
            # Reconstruct the file
            # Start with the header part (before first ##)
            lines = current_content.split('\n')
            header_lines = []
            for line in lines:
                if line.startswith('## '):
                    break
                header_lines.append(line)
            
            # Build new content
            new_content = '\n'.join(header_lines).rstrip() + '\n\n'
            
            # Add sections in original order (preserve structure)
            section_order = list(current_sections.keys())
            for section_name in section_order:
                if section_name in fixed_sections:
                    new_content += fixed_sections[section_name] + '\n\n'
            
            # Add any completely new sections at the end
            for section_name in fixed_sections.keys():
                if section_name not in section_order:
                    new_content += fixed_sections[section_name] + '\n\n'
            
            # Write the fixed content
            current_path.write_text(new_content.rstrip() + '\n', encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return False

def fix_all_transcripts():
    """Fix all transcripts by comparing with originals."""
    transcript_folder = Path("transcripts")
    original_folder = Path("originals")
    
    if not transcript_folder.exists():
        print("❌ Transcripts folder not found: transcripts/")
        return
    
    if not original_folder.exists():
        print("❌ Originals folder not found: originals/")
        return
    
    print("TRANSCRIPT CONTENT RESTORER")
    print("=" * 50)
    print("Comparing current transcripts with originals...\n")
    
    fixed_count = 0
    total_count = 0
    
    for file_path in transcript_folder.glob("*.md"):
        filename = file_path.name
        total_count += 1
        
        print(f"📄 Processing: {filename}")
        
        if compare_and_fix_transcript(filename):
            print(f"   ✅ Fixed missing content")
            fixed_count += 1
        else:
            print(f"   ✅ No changes needed")
    
    print(f"\n" + "=" * 50)
    print(f"📊 Summary: Fixed {fixed_count} out of {total_count} files")
    
    if fixed_count > 0:
        print(f"🎉 Successfully restored missing content in {fixed_count} transcript(s)!")
    else:
        print("✅ All transcripts appear to be complete!")

if __name__ == "__main__":
    fix_all_transcripts()