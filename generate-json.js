// generate-json.js

const fs = require('fs');
const path = require('path');

// Define the directory where your MD files are stored and the output JSON file path.
const transcriptsDir = path.join(__dirname, 'transcripts');
const outputFile = path.join(__dirname, 'transcripts.json');

// Read all files in the transcripts directory that end with '.md'
const transcriptFiles = fs.readdirSync(transcriptsDir).filter(file => file.endsWith('.md'));

const transcripts = transcriptFiles.map(file => {
  const filePath = path.join(transcriptsDir, file);
  const content = fs.readFileSync(filePath, 'utf8');

  // Extract title from the first Markdown heading (e.g., "# 29 March 2025")
  let title = file;
  const titleMatch = content.match(/^#\s+(.*)/);
  if (titleMatch) {
    title = titleMatch[1].trim();
  }

  // Optionally extract tags from a line starting with "**Tags:**"
  let tags = "";
  const tagsMatch = content.match(/\*\*Tags:\*\*\s*(.*)/);
  if (tagsMatch) {
    tags = tagsMatch[1].trim();
  }

  return {
    file: file,
    title: title,
    tags: tags,
    content: content
  };
});

// Write the transcripts array to a JSON file with pretty-printing
fs.writeFileSync(outputFile, JSON.stringify(transcripts, null, 2));
console.log(`Generated ${outputFile} with ${transcripts.length} transcripts.`);
