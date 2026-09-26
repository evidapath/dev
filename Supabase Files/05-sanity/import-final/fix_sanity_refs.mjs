import fs from "fs";

const INPUT = "five-school-sanity-drafts.resolved.ndjson";
const OUTPUT = "five-school-sanity-drafts.references-fixed.ndjson";

let changedRefs = 0;
let documentCount = 0;

function fixRefs(value) {
  if (Array.isArray(value)) {
    return value.map(fixRefs);
  }

  if (value && typeof value === "object") {
    const result = {};

    for (const [key, val] of Object.entries(value)) {
      if (
        key === "_ref" &&
        typeof val === "string" &&
        val.startsWith("drafts.")
      ) {
        result[key] = val.slice("drafts.".length);
        changedRefs++;
      } else {
        result[key] = fixRefs(val);
      }
    }

    return result;
  }

  return value;
}

const lines = fs
  .readFileSync(INPUT, "utf8")
  .split(/\r?\n/)
  .filter(line => line.trim() !== "");

const output = lines.map((line, index) => {
  const doc = JSON.parse(line);
  const originalId = doc._id;

  const fixed = fixRefs(doc);

  if (fixed._id !== originalId) {
    throw new Error(
      `Document _id changed unexpectedly on line ${index + 1}: ${originalId} -> ${fixed._id}`
    );
  }

  documentCount++;
  return JSON.stringify(fixed);
});

fs.writeFileSync(OUTPUT, output.join("\n") + "\n", "utf8");

console.log(`Documents written: ${documentCount}`);
console.log(`Draft-prefixed references fixed: ${changedRefs}`);
console.log(`Output: ${OUTPUT}`);