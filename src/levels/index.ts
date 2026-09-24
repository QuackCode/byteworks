export interface Level {
  day: number;
  title: string;
  topic: string;
  floor: number;
  machine: string;
  briefing: string;
  hints: string[];
  bonus: string;
  lesson: string;
  starter: string;
  check: string;
}

// Each level lives in its own folder (dayNN/) so the Python files can be tested with plain Python too.
const files = import.meta.glob("./day*/*.{json,md,py}", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

function buildLevels(): Level[] {
  const byDir = new Map<string, Record<string, string>>();
  for (const [path, text] of Object.entries(files)) {
    const [, dir, file] = path.split("/");
    if (!byDir.has(dir)) byDir.set(dir, {});
    byDir.get(dir)![file] = text;
  }
  const levels: Level[] = [];
  for (const parts of byDir.values()) {
    if (!parts["meta.json"]) continue;
    levels.push({
      ...JSON.parse(parts["meta.json"]),
      lesson: parts["lesson.md"],
      starter: parts["starter.py"],
      check: parts["check.py"],
    });
  }
  return levels.sort((a, b) => a.day - b.day);
}

export const LEVELS = buildLevels();
