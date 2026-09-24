import type { WorldState } from "./types";

export interface Settings { speed: number; follow: boolean; skin?: string }
export interface Save { v: 2; world: WorldState | null; files: Record<string, string>; active: string; settings: Settings }

const KEY = "byteworks.save.v2";

export const STARTER = `# Welcome to ByteWorks! Press Run (or Ctrl+Enter).
# Your drone harvests the RAM stick under it, moves East, then harvests again.
harvest()
move(East)
harvest()
`;

export const emptySave = (): Save => ({
  v: 2, world: null, files: { "main.py": STARTER }, active: "main.py", settings: { speed: 1, follow: true },
});

function isSave(x: unknown): x is Save {
  const s = x as Save;
  return !!s && s.v === 2
    && typeof s.files === "object" && s.files !== null
    && Object.values(s.files).every((v) => typeof v === "string") && "main.py" in s.files
    && typeof s.active === "string" && s.active in s.files
    && !!s.settings && typeof s.settings.speed === "number" && typeof s.settings.follow === "boolean"
    && (s.world === null || (typeof s.world === "object" && "inventory" in s.world && "floors" in s.world));
}

export function loadSave(): Save {
  try {
    const parsed = JSON.parse(localStorage.getItem(KEY) ?? "null");
    return isSave(parsed) ? parsed : emptySave();
  } catch {
    return emptySave();
  }
}

export function storeSave(save: Save): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(save));
  } catch {
    /* storage blocked or full: progress just won't persist */
  }
}

export function encodeSave(save: Save): string {
  const bytes = new TextEncoder().encode(JSON.stringify(save));
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return "BW2." + btoa(binary);
}

export function decodeSave(code: string): Save | null {
  try {
    const trimmed = code.trim();
    if (!trimmed.startsWith("BW2.")) return null;
    const bytes = Uint8Array.from(atob(trimmed.slice(4)), (c) => c.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    return isSave(parsed) ? parsed : null;
  } catch {
    return null;
  }
}
