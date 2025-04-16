// fixMarkdownSeparators.js

const fs = require('fs');
const path = require('path');

const inputFile = path.join(__dirname, 'transcripts.json');
const outputFile = path.join(__dirname, 'transcripts_fixed.json');

/**
 * Insert a separator ("---") before headings if missing,
 * BUT skip the very first heading in the file.
 */
function insertSeparatorsSkippingFirstHeading(rawMarkdown) {
  const lines = rawMarkdown.split('\n');
  const newLines = [];

  let foundFirstHeading = false;

  for (let i = 0; i < lines.length; i++) {
    const currentLine = lines[i];

    // Check if current line is a heading (starts with at least "## ").
    if (/^#{2,}\s/.test(currentLine)) {
      if (!foundFirstHeading) {
        // This is the very first heading we encounter; do NOT insert a separator.
        foundFirstHeading = true;
      } else {
        // For subsequent headings, check if the previous line is a separator or blank.
        // If not, insert "---".
        if (newLines.length > 0) {
          // Move backward to find the most recent non-empty line
          let j = newLines.length - 1;
          while (j >= 0 && newLines[j].trim() === '') {
            j--;
          }
          const prevLine = j >= 0 ? newLines[j].trim() : '';
          if (prevLine !== '---') {
            newLines.push('---');
          }
        }
      }
    }

    newLines.push(currentLine);
  }

  return newLines.join('\n');
}

fs.readFile(inputFile, 'utf8', (err, data) => {
  if (err) {
    console.error('Error reading transcripts.json:', err);
    process.exit(1);
  }

  let transcripts;
  try {
    transcripts = JSON.parse(data);
  } catch (parseErr) {
    console.error('Error parsing JSON:', parseErr);
    process.exit(1);
  }

  // Process each transcript's content.
  transcripts = transcripts.map(transcript => {
    transcript.content = insertSeparatorsSkippingFirstHeading(transcript.content);
    return transcript;
  });

  // Write the updated transcripts to a new JSON file.
  fs.writeFile(outputFile, JSON.stringify(transcripts, null, 2), 'utf8', err => {
    if (err) {
      console.error('Error writing fixed transcripts file:', err);
      process.exit(1);
    }
    console.log(`Updated transcripts written to ${outputFile}`);
  });
});
