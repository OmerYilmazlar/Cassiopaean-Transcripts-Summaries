import os
import re
import json
from pathlib import Path

# Change working directory to the project root
os.chdir(Path(__file__).parent.parent)

INPUT_FOLDER  = "transcripts"
OUTPUT_FOLDER = "transcripts"
JSON_OUTPUT   = "transcripts.json"
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

# 1) “No-info” phrases
KEYWORDS = [
    "no direct content under this heading in this session",
    "no specific content under this heading",
    "no direct alien contact or interaction information discussed in this session",
    "no content under this heading",
    "no content under this category in this session",
    "no specific points under this session",
    "none","none noted","none mentioned","none directly discussed","none discussed",
    "n a","not applicable","not covered","not discussed",
    "no historical insights explored beyond the holy grail reference",
    "no discussion of political power structures in this session",
    "no industrial events mentioned",
    "no content applicable","no specific references",
    "no direct contact or alien interaction discussed in this session",
    "no specific spiritual rituals or practices discussed",
    "no discussion under this topic in this session",
    "no explicit historical insights mentioned",
    "no specific content under this section in this session",
    "not addressed in this session","no notable content",
    "(no direct references in this session)","no direct references under this topic",
    "no significant content under this topic in this session","no direct references in this session",
    "no content under this section for this session",
    "not covered","no discussion of health","no content under this",
    "no direct mention of specific books","no direct mention of health, diet, or supplements",
    "not covered beyond soul group lineage mention of caesar and putin",
    "no direct mention of ritual or structured spiritual practice","not addressed",
    "no content under this category in this session","not discussed in this session",
    "no specific afterlife","no specific earth","no specific health","no specific events",
    "no specific discussion","no specific content","no specific book",
    "no references to religious relics or preservation efforts",
    "no historical timelines or insights explored in this session",
    "no direct discussion on governments or global political agendas",
    "no mention of industrial or ecological disasters or conspiracies",
    "none explicitly mentioned","no direct discussion","no direct alien contact discussed",
    "no content under this category","(not applicable in this session)",
    "no content under this topic in this session","n/a",
    "no content under this section in this session","no content in this category",
    "no additional historical context provided beyond wwii/usa comparison",
    "(no content relevant to this section.)","no direct content on this topic in this session",
    "no relevant content","(not directly applicable in this session)",
    "(discussed within \"control system & sociopolitical manipulation\")",
    "(covered under \"earth changes & environmental events\")",
    "(no content in this section for this session.)","no direct content under this category",
    "no specific spiritual practices discussed in this session",
    "(no relevant content in this session)","no direct et contact discussed",
    "no specific content under this category in this session",
    "(no content in this category for this session.)","none explicitly mentioned in this session",
    "no specific discussion under this category in this session","no direct statements",
    # extras
    "no relevant earth or cosmic events discussed",
    "no earth changes or environmental events discussed",
    "no significant discussion under this category",
    "no relevant content under this section in this session",
    "no direct mentions in this session",
    "no discussion on physical health, diet, or supplements took place in this session",
    "no direct commentary on physical health, diet, or supplements",
    "no significant content on this topic in this session",
    "no mention of physical health, diet, or supplements in this session",
    "no discussion in this session directly addressing control systems or sociopolitical manipulation",
    "no books or media titles were discussed",
    "no direct alien contact or interaction information discussed in this session",
    "no direct alien contact or hyperdimensional interactions discussed in this session"
]
KEYWORDS = [k.lower() for k in KEYWORDS]

# Regex patterns
SECTION_SPLIT_RE    = re.compile(r'(?=^## )', re.MULTILINE)
BULLET_RE           = re.compile(r'^\s*[-*+]\s+(.*)')
HEADING_DEEP_RE     = re.compile(r'^(#{3,})\s+(.*)$')
SUMMARY_RE          = re.compile(r'##.*?Summary.*?\((https?://[^\)]+)\)')
# capture the colon+rest of the Zoom line
ZOOM_LINE_RE        = re.compile(
    r'^\s*\*\*FOTCM\s+Zoom\s+attendees\s*:\*\*(.*)$',
    re.IGNORECASE
)

def clean_sections(text: str) -> str:
    parts, out = SECTION_SPLIT_RE.split(text), []
    for part in parts:
        if part.startswith("## "):
            lines = part.splitlines(keepends=True)
            kept = []
            for L in lines:
                m = BULLET_RE.match(L)
                if m and any(kw in m.group(1).lower() for kw in KEYWORDS):
                    continue
                kept.append(L)
            has_bullet = any(BULLET_RE.match(L) for L in kept)
            has_other  = any(
                not re.match(r'^\s*(#{1,2}\s+|[-*+]\s+|---\s*$)', L) and L.strip()
                for L in kept
            )
            if has_bullet or has_other:
                out.append("".join(kept))
        else:
            out.append(part)
    return "".join(out)

def standardize(text: str, session_date: str) -> str:
    lines, out, fixed_summary = text.splitlines(keepends=True), [], False
    for L in lines:
        # 1) flatten deep headings → ##
        m = HEADING_DEEP_RE.match(L)
        if m:
            L = f"## {m.group(2)}\n"
        # 2) fix summary link once
        if not fixed_summary and "Summary" in L and "(" in L:
            sm = SUMMARY_RE.match(L)
            if sm:
                url = sm.group(1)
                L = f"## Summary of [{session_date} Cassiopaean Session]({url})\n"
                fixed_summary = True
        # 3) rename Zoom but keep attendee list
        zm = ZOOM_LINE_RE.match(L)
        if zm:
            rest = zm.group(1).strip()
            L = f"**FOTCM Members via Zoom:**{(' ' + rest) if rest else ''}\n"
        out.append(L)
    return "".join(out)

def insert_separators(text: str) -> str:
    lines, new = text.splitlines(), []
    first_h = False
    for line in lines:
        if line.startswith("## "):
            if not first_h:
                first_h = True
            else:
                j = len(new)-1
                while j>=0 and new[j].strip()=="":
                    j -= 1
                if j>=0 and new[j].strip()!="---":
                    new.append("---")
        new.append(line)
    return "\n".join(new)+"\n"

def process_file(in_path: Path):
    txt      = in_path.read_text(encoding="utf-8")
    cleaned  = clean_sections(txt)
    # get session date from first line "# 25 January 2025"
    first    = cleaned.splitlines()[0]
    m        = re.match(r'^#\s+(.*)', first)
    session_date = m.group(1).strip() if m else ""
    std      = standardize(cleaned, session_date)
    final    = insert_separators(std)
    return final

def main():
    all_transcripts = []
    for fn in os.listdir(INPUT_FOLDER):
        if not fn.lower().endswith(".md"):
            continue
        path = Path(INPUT_FOLDER)/fn
        content = process_file(path)
        # overwrite
        path.write_text(content, encoding="utf-8")
        # extract title & tags
        title_match = re.match(r'^#\s+(.*)', content.splitlines()[0])
        title = title_match.group(1).strip() if title_match else fn
        tags_match = re.search(r'\*\*Tags:\*\*\s*(.*)', content)
        tags = tags_match.group(1).strip() if tags_match else ""
        all_transcripts.append({
            "file": fn,
            "title": title,
            "tags": tags,
            "content": content
        })
        print(f"→ Processed: {fn}")

    # write JSON
    with open(JSON_OUTPUT, "w", encoding="utf-8") as jf:
        json.dump(all_transcripts, jf, ensure_ascii=False, indent=2)
    print(f"Generated {JSON_OUTPUT} with {len(all_transcripts)} transcripts.")

if __name__ == "__main__":
    main()