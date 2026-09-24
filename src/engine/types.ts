export type Tile = [part: string | null, readyAt: number, faulty: boolean, score: number | null, plantedAt: number];
export interface FloorState { size: number; grid: Tile[][] }            // grid[x][y], y = 0 is South
export interface WorldState {
  seed: number; clock: number; inventory: Record<string, number>; unlocks: string[]; speed_level: number;
  floors: Record<string, FloorState>; floor: string; x: number; y: number;
  order: Record<string, number> | null; orders_done: number; bumped?: boolean; quests?: string[]; rng: unknown;
}
export interface UnlockInfo {
  id: string; title: string; cost: Record<string, number>; requires: string[]; summary: string;
  help: string | null; kind: "feature" | "floor" | "grid" | "speed" | "other"; windows: number;
  quest: { id: string; title: string; page: string } | null;
}
export interface RunResult { ok: boolean; stopped: boolean; error?: string; state: WorldState }
export interface BuyResult { ok: boolean; message: string; state: WorldState }
export interface SnippetResult { stdout: string; error: string | null }
export type RunnerStatus = "loading" | "ready" | "failed";
