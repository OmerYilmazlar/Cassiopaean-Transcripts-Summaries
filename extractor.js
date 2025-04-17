const fs = require("fs");

// List of target headers to process.
const TARGET_HEADERS = [
    "Contact and Alien Interactions",
    "Spiritual Practices & Ritual",
    "Genetics and Ancestry",
    "Religious and Historical Preservation",
    "Historical Insights",
    "Political Power Structures",
    "Environmental & Industrial Events"
];

// Regex to match a Markdown header (e.g., "## Header Name").
const HEADER_REGEX = /^##\s*(.+?)\s*$/i;

/**
 * Extracts sections from the markdown content where the header is one of the TARGET_HEADERS.
 * For each target header, captures lines until a new header or horizontal rule ("---") is found.
 * Returns an object mapping target headers to their single-line content if exactly one nonempty line is found.
 *
 * @param {string} markdownContent - The complete markdown content.
 * @returns {Object} An object mapping header names to their single bullet point content.
 */
function extractTargetSections(markdownContent) {
    const lines = markdownContent.split("\n");
    const results = {};
    let i = 0;
    while (i < lines.length) {
        const line = lines[i].trim();
        const headerMatch = line.match(HEADER_REGEX);
        if (headerMatch) {
            const headerName = headerMatch[1].trim();
            if (TARGET_HEADERS.includes(headerName)) {
                const sectionLines = [];
                i++; // move to the lines after the header
                // Collect lines until next header or a horizontal rule is reached.
                while (i < lines.length) {
                    const currentLine = lines[i].trim();
                    if (currentLine.startsWith("##") || currentLine.startsWith("---")) {
                        break;
                    }
                    if (currentLine !== "") {
                        sectionLines.push(currentLine);
                    }
                    i++;
                }
                // Only save if exactly one nonempty line (a single bullet point) was found.
                if (sectionLines.length === 1) {
                    results[headerName] = sectionLines[0];
                }
            } else {
                i++;
            }
        } else {
            i++;
        }
    }
    return results;
}

function main() {
    // Read transcripts from the JSON file.
    fs.readFile("transcripts.json", "utf8", (err, data) => {
        if (err) {
            console.error("Error reading transcripts.json:", err);
            return;
        }
        let transcripts;
        try {
            transcripts = JSON.parse(data);
        } catch (e) {
            console.error("Error parsing JSON:", e);
            return;
        }
        const extractedSections = [];
        // Process each transcript.
        transcripts.forEach(transcript => {
            const fileName = transcript.file || "";
            const content = transcript.content || "";
            const sections = extractTargetSections(content);
            for (const header in sections) {
                extractedSections.push({
                    file: fileName,
                    header: header,
                    content: sections[header]
                });
            }
        });
        // Write the full extraction to a file.
        fs.writeFile("extracted_sections.json", JSON.stringify(extractedSections, null, 4), "utf8", err => {
            if (err) {
                console.error("Error writing extracted_sections.json:", err);
            } else {
                console.log("Extraction complete. Results saved to extracted_sections.json");
            }
        });

        // Now, build a set of unique bullet content entries.
        const uniqueContentSet = new Set();
        extractedSections.forEach(entry => {
            // Optionally, you might want to normalize whitespace.
            uniqueContentSet.add(entry.content.trim());
        });
        const uniqueEntries = Array.from(uniqueContentSet);
        // Write the unique bullet entries to a separate JSON file.
        fs.writeFile("unique_bullet_entries.json", JSON.stringify(uniqueEntries, null, 4), "utf8", err => {
            if (err) {
                console.error("Error writing unique_bullet_entries.json:", err);
            } else {
                console.log("Unique bullet entries saved to unique_bullet_entries.json");
            }
        });
    });
}

main();
