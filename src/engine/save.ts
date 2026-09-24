export interface Save {
  v: 1;
  completed: number[];
  code: Record<string, string>; // day -> the player's code
}

const KEY = "byteworks.save.v1";

export const emptySave = (): Save => ({ v: 1, completed: [], code: {} });

function isSave(x: unknown): x is Save {
  const s = x as Save;
  return !!s && s.v === 1 && Array.isArray(s.completed) && s.completed.every(Number.isInteger)
    && typeof s.code === "object" && s.code !== null;
}

// Browser storage can be missing or blocked (private windows), so every access is guarded.
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
    /* progress just won't persist */
  }
}

/** A copy-pasteable save code, so players can move progress between devices. */
export function encodeSave(save: Save): string {
  const bytes = new TextEncoder().encode(JSON.stringify(save));
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return "BW1." + btoa(binary);
}

export function decodeSave(code: string): Save | null {
  try {
    const trimmed = code.trim();
    if (!trimmed.startsWith("BW1.")) return null;
    const binary = atob(trimmed.slice(4));
    const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    return isSave(parsed) ? parsed : null;
  } catch {
    return null;
  }
}
