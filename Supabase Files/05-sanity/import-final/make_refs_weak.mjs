import fs from "fs";

const INPUT = "five-school-sanity-drafts.references-fixed.ndjson";
const OUTPUT = "five-school-sanity-drafts.staging-ready.ndjson";

let referenceCount = 0;
let documentCount = 0;

function makeRefsWeak(value) {
  if (Array.isArray(value)) {
    return value.map(makeRefsWeak);
  }

  if (value && typeof value === "object") {
    const result = {};

    for (const [key, val] of Object.entries(value)) {
      result[key] = makeRefsWeak(val);
    }

    if (
      result._type === "reference" &&
      typeof result._ref === "string"
    ) {
      result._weak = true;
      referenceCount++;
    }

    return result;
  }

  return value;
}

const lines = fs
  .readFileSync(INPUT, "utf8")
  .split(/\r?\n/)
  .filter(line => line.trim());

const output = lines.map((line, index) => {
  const doc = JSON.parse(line);
  const originalId = doc._id;

  const fixed = makeRefsWeak(doc);

  if (fixed._id !== originalId) {
    throw new Error(
      `Document _id changed on line ${index + 1}: ${originalId} -> ${fixed._id}`
    );
  }

  documentCount++;
  return JSON.stringify(fixed);
});

fs.writeFileSync(OUTPUT, output.join("\n") + "\n", "utf8");

console.log(`Documents written: ${documentCount}`);
console.log(`References marked weak: ${referenceCount}`);
console.log(`Output: ${OUTPUT}`);