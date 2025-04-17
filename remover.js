const fs = require("fs");

// Define target headers for which we want to check and possibly remove their sections.
const TARGET_HEADERS = [
    "Contact and Alien Interactions",
    "Spiritual Practices & Ritual",
    "Genetics and Ancestry",
    "Religious and Historical Preservation",
    "Historical Insights",
    "Political Power Structures",
    "Environmental & Industrial Events",
    "Afterlife & Soul Topics",
    "Cosmic Structure & Densities",
    "Earth Changes & Environmental Events",
    "Health, Diet, and Supplements",
    "Control System & Sociopolitical Manipulation",
    "Esoteric Work & Personal Development",
    "Books, Research, and Cultural Commentary",
    "Notable Warnings or Predictions",
    "Technology and Artificial Intelligence"
];

// List of no-information phrases (normalized: lower-case, no punctuation)
const NO_INFO_PHRASES = [
    "no direct content under this heading in this session",
    "no specific content under this heading",
    "no direct alien contact or interaction information discussed in this session",
    "no content under this heading",
    "no content under this category in this session",
    "no specific points under this session",
    "none",
    "none noted",
    "none mentioned",
    "None directly discussed",
    "none discussed",
    "n a",
    "not applicable",
    "not covered",
    "not discussed",
    "No direct content under this heading in this session",
    "No specific content under this heading",
    "No direct alien contact or interaction information discussed in this session",
    "No historical insights explored beyond the Holy Grail reference",
    "No discussion of political power structures in this session",
    "No industrial events mentioned",
    "No content under this heading in this session",
    "No specific points under this session",
    "No content applicable",
    "No specific references",
    "None",
    "No direct contact or alien interaction discussed in this session",
    "No specific spiritual rituals or practices discussed",
    "No discussion under this topic in this session",
    "No explicit historical insights mentioned",
    "No specific content under this section in this session",
    "Not addressed in this session",
    "No content under this heading",
    "No notable content",
    "(No direct references in this session)",
    "No direct references under this topic",
    "No significant content under this topic in this session",
    "No direct references in this session",
    "No content under this section for this session",
    "Not covered",
    "Not covered beyond soul group lineage mention of Caesar and Putin",
    "No direct mention of ritual or structured spiritual practice",
    "Not addressed",
    "No content under this category in this session",
    "Not discussed in this session",
    "None mentioned",
    "No specific content under this category in this session",
    "No direct content in this section",
    "(No significant content in this session)",
    "[Not covered]",
    "No direct content under this category",
    "No direct references in this session",
    "No content under this section for this session",
    "Not discussed",
    "No specific afterlife",
    "No specific earth",
    "no specific health",
    "No specific events",
    "No specific discussion",
    "No specific content",
    "No specific book",
    "No specific references",
    "No specific content under this heading in this session",
    "No explicit discussion of genetic topics",
    "No explicit",
    "No references to religious relics or preservation efforts",
    "No historical timelines or insights explored in this session",
    "No direct discussion on governments or global political agendas",
    "No mention of industrial or ecological disasters or conspiracies",
    "None explicitly mentioned",
    "No direct alien contact discussed",
    "No content under this category",
    "(Not applicable in this session)",
    "No content under this topic in this session",
    "N/A",
    "No content under this section in this session",
    "No content in this category",
    "No additional historical context provided beyond WWII/USA comparison",
    "(No specific content under this category in this session)",
    "No content in this session",
    "(No content relevant to this section.)",
    "No direct content on this topic in this session",
    "No relevant content",
    "(Not directly applicable in this session)",
    "(Discussed within \"Control System & Sociopolitical Manipulation\")",
    "(Covered under \"Earth Changes & Environmental Events\")",
    "(No content in this section for this session.)",
    "No direct content under this category",
    "No specific spiritual practices discussed in this session",
    "No direct references in this session",
    "No content under this section for this session",
    "Not discussed",
    "(No relevant content in this session)",
    "No direct alien contact discussed",
    "No content under this category",
    "No additional historical context provided beyond WWII/USA comparison",
    "(No specific content under this category in this session)",
    "No content in this session",
    "(No content relevant to this section.)",
    "No direct content on this topic in this session",
    "(Not directly applicable in this session)",
    "No content under this category in this session",
    "(No significant content in this session)",
    "No direct content under this heading in this session",
    "No direct content under this category in this session",
    "No explicit discussion of genetic topics",
    "No references to religious relics or preservation efforts",
    "No historical timelines or insights explored in this session",
    "No direct discussion on governments or global political agendas",
    "No mention of industrial or ecological disasters or conspiracies",
    "None explicitly mentioned",
    "No direct discussion",
    "No direct alien contact discussed",
    "No content under this category",
    "No additional historical context provided beyond WWII/USA comparison",
    "(No specific content under this category in this session)",
    "No content in this session",
    "(No content relevant to this section.)",
    "No direct content on this topic in this session",
    "(Not directly applicable in this session)",
    "No content under this category",
    "(No significant content in this session)",
    "No direct content under",
    "No direct content in",
    "No direct ET contact discussed",
    "No content under this category",
    "No specific content under this category in this session",
    "(No content in this category for this session.)",
    "None explicitly mentioned in this session",
    "No specific discussion under this category in this session",
    "No direct statements"
];

// Regular expression to match Markdown header lines (e.g., "## Header Name")
const HEADER_REGEX = /^##\s*(.+?)\s*$/i;

// Function to normalize text for comparison
function normalizeText(text) {
    // Remove bullet point markers (like "- " or "* ")
    let normalized = text.replace(/^[-*•]\s+/, "");
    // Convert to lowercase
    normalized = normalized.toLowerCase();
    // Remove trailing periods
    normalized = normalized.replace(/\.$/, "");
    // Trim whitespace
    return normalized.trim();
}

// Pre-normalize all phrases for more efficient comparison
const NORMALIZED_NO_INFO_PHRASES = NO_INFO_PHRASES.map(phrase => {
    return normalizeText(phrase);
});

// Function that checks if a given text contains any of the no-information phrases after normalization.
function isNoInformation(text) {
    const normalizedText = normalizeText(text);
    // Check if any of our phrases are contained within the text
    return NORMALIZED_NO_INFO_PHRASES.some(phrase => normalizedText.includes(phrase));
}

/**
 * Processes Markdown content and removes the entire section corresponding to a target header
 * if the section's nonblank content (after the header) consists of exactly one line that is a no-information phrase.
 */
function removeNoInfoSections(markdownContent) {
    const lines = markdownContent.split("\n");
    let outputLines = [];
    let i = 0;
    let lastLineWasSeparator = false;

    while (i < lines.length) {
        const line = lines[i];
        
        // Check if current line is a separator
        const isSeparator = line.trim() === "---";
        
        // Handle separators - avoid consecutive separators
        if (isSeparator) {
            if (!lastLineWasSeparator && outputLines.length > 0) {
                outputLines.push(line);
                lastLineWasSeparator = true;
            }
            i++;
            continue;
        }
        
        const headerMatch = line.match(HEADER_REGEX);
        if (headerMatch) {
            // Found a header; get header text.
            const headerName = headerMatch[1].trim();
            if (TARGET_HEADERS.includes(headerName)) {
                // We're in one of our target headers – capture its section.
                let sectionStart = i; // Mark the start position of this section
                i++; // Move past the header
                let contentLines = [];
                
                // Capture content until next header
                while (i < lines.length && !lines[i].startsWith("##")) {
                    const currentLine = lines[i];
                    if (currentLine.trim() !== "" && currentLine.trim() !== "---") {
                        contentLines.push(currentLine.trim());
                    }
                    i++;
                }
                
                // If exactly one nonblank content line exists (ignoring separators), check if it is a "no information" phrase.
                if (contentLines.length === 1 && isNoInformation(contentLines[0])) {
                    // Skip this section entirely - we're already positioned at the next header or EOF
                    // Reset separator flag since we're skipping content
                    lastLineWasSeparator = false;
                } else {
                    // Otherwise, preserve this section.
                    // Add the header
                    outputLines.push(lines[sectionStart]);
                    // Add all content from after header up to (but not including) the next header
                    for (let j = sectionStart + 1; j < i; j++) {
                        outputLines.push(lines[j]);
                    }
                    lastLineWasSeparator = lines[i-1].trim() === "---";
                }
            } else {
                // Header not in target, simply include it.
                outputLines.push(line);
                lastLineWasSeparator = false;
                i++;
            }
        } else {
            // Not a header or separator, just add the line
            outputLines.push(line);
            lastLineWasSeparator = false;
            i++;
        }
    }
    
    // Clean up any trailing separator
    while (outputLines.length > 0 && outputLines[outputLines.length - 1].trim() === "---") {
        outputLines.pop();
    }
    
    return outputLines.join("\n");
}

function main() {
    fs.readFile("transcripts.json", "utf8", (err, data) => {
        if (err) {
            console.error("Error reading transcripts.json:", err);
            return;
        }
        let transcripts;
        try {
            transcripts = JSON.parse(data);
        } catch (parseErr) {
            console.error("Error parsing JSON:", parseErr);
            return;
        }
        // Process each transcript's content.
        transcripts.forEach(transcript => {
            if (transcript.content) {
                transcript.content = removeNoInfoSections(transcript.content);
            }
        });
        // Write the improved transcripts to transcripts.json
        fs.writeFile("transcripts.json", JSON.stringify(transcripts, null, 4), "utf8", (writeErr) => {
            if (writeErr) {
                console.error("Error writing transcripts.json:", writeErr);
            } else {
                console.log("Improved transcripts saved to transcripts.json");
            }
        });
    });
}

main();