import type { Tile } from "../engine/types";

export interface TileLook { part: string | null; ready: boolean; progress: number; faulty: boolean; score: number | null }
export interface DronePos { floor: string; x: number; y: number }

export function lookOf(tile: Tile, clock: number): TileLook {
  const [part, readyAt, faulty, score, plantedAt] = tile;
  if (part === null) return { part: null, ready: false, progress: 0, faulty: false, score: null };
  const ready = clock >= readyAt;
  const progress = ready ? 1 : Math.min(1, Math.max(0, (clock - plantedAt) / Math.max(1, readyAt - plantedAt)));
  return { part, ready, progress, faulty: part === "BOARD" && ready && faulty, score: part === "GPU" ? score : null };
}

/** How long the drone should glide to its new spot: no glide when it jumps (lift, loaded save) or changes floor. */
export function moveDuration(prev: DronePos | null, next: DronePos, animMs: number): number {
  if (!prev || prev.floor !== next.floor) return 0;
  if (Math.abs(prev.x - next.x) > 1 || Math.abs(prev.y - next.y) > 1) return 0;
  return animMs;
}

/** SVG rows count down from the top, but North (+y) is up on screen. */
export function svgRow(y: number, size: number): number {
  return size - 1 - y;
}

/** The drone's new heading in degrees (0 = North, clockwise), turning the short way round.
 *  Headings accumulate past 360 so the CSS rotation never spins the long way. */
export function nextHeading(prev: DronePos | null, next: DronePos, heading: number): number {
  if (!prev || prev.floor !== next.floor) return heading;
  const dx = next.x - prev.x;
  const dy = next.y - prev.y;
  if (dx === 0 && dy === 0) return heading;
  const target = (Math.atan2(dx, dy) * 180) / Math.PI;    // North = 0, East = 90
  let delta = ((((target - heading) % 360) + 540) % 360) - 180;
  if (delta === -180) delta = 180;                         // a U-turn goes clockwise
  return heading + delta;
}
