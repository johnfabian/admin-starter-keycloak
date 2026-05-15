import { mkdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";

const rawTitle = process.argv.slice(2).join(" ").trim() || "implementation-plan";
const slug =
  rawTitle
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "implementation-plan";

const today = new Date().toISOString().slice(0, 10);
const plansDir = path.join(process.cwd(), "specs", "plans");

function planPathFor(index) {
  const suffix = index === 1 ? "" : `-${index}`;
  return path.join(plansDir, `${today}-${slug}${suffix}.md`);
}

let index = 1;
let filePath = planPathFor(index);
while (existsSync(filePath)) {
  index += 1;
  filePath = planPathFor(index);
}

const title = rawTitle
  .split(/[\s-_]+/)
  .filter(Boolean)
  .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
  .join(" ");

const content = `# ${title}

Date: ${today}

## Summary

TBD

## Key Changes

- TBD

## Public Interfaces / Config

- TBD

## Test Plan

- TBD

## Assumptions

- TBD

## Implementation Status

- Planned
`;

await mkdir(plansDir, { recursive: true });
await writeFile(filePath, content, { encoding: "utf8", flag: "wx" });

console.log(path.relative(process.cwd(), filePath).replaceAll(path.sep, "/"));
