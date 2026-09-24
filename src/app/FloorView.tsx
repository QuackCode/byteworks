import { useRef } from "preact/hooks";
import type { WorldState } from "../engine/types";
import { PART_ICON, WIN_COMPUTERS, type FloorInfo } from "../floors";
import { lookOf, moveDuration, svgRow, type DronePos } from "./floorMath";

const CELL = 100;

interface Props { floor: FloorInfo; world: WorldState; animMs: number; locked: boolean; lockedBy: string }

export function FloorView({ floor, world, animMs, locked, lockedBy }: Props) {
  const prev = useRef<DronePos | null>(null);
  const state = world.floors[floor.id];
  if (locked || !state) {
    return (
      <div class="floor-locked">
        <div class="floor-locked-icon">🔒</div>
        <div>{floor.name} is locked</div>
        <small>Buy “{lockedBy}” in the Upgrades tree.</small>
      </div>
    );
  }
  if (floor.id === "ASSEMBLY") return <AssemblyView world={world} />;

  const n = state.size;
  const pos = { floor: world.floor, x: world.x, y: world.y };
  const duration = moveDuration(prev.current, pos, animMs);
  prev.current = pos;

  return (
    <svg class="floor-svg" viewBox={`0 0 ${n * CELL} ${n * CELL}`} role="img" aria-label={`${floor.name}: ${n} by ${n} grid`}
      style={{ "--floor": floor.color }}>
      {state.grid.map((column, x) => column.map((tile, y) => {
        const look = lookOf(tile, world.clock);
        return (
          <g key={`${x}-${y}`} transform={`translate(${x * CELL} ${svgRow(y, n) * CELL})`}>
            <rect x="4" y="4" width="92" height="92" rx="10" class={`tile${look.ready ? " ready" : ""}${look.faulty ? " faulty" : ""}`} />
            {look.part && <text x="50" y="62" text-anchor="middle" class="tile-icon" opacity={look.ready ? 1 : 0.4}>{PART_ICON[look.part]}</text>}
            {look.part && !look.ready && <rect x="14" y="80" width={72 * look.progress} height="7" rx="3" class="grow-bar" />}
            {look.faulty && <text x="74" y="32" class="tile-flag">⚠️</text>}
            {look.score !== null && <text x="84" y="28" text-anchor="middle" class="tile-score">{look.score}</text>}
          </g>
        );
      }))}
      {world.floor === floor.id && (
        <g class="drone" style={{ transform: `translate(${world.x * CELL}px, ${svgRow(world.y, n) * CELL}px)`, transitionDuration: `${duration}ms` }}>
          <g class={world.bumped ? "drone-body bumped" : "drone-body"}>
            <circle cx="50" cy="50" r="36" class="drone-ring" />
            <text x="50" y="64" text-anchor="middle" class="drone-icon">🤖</text>
            {world.bumped && <text x="50" y="16" text-anchor="middle" class="drone-stun">💫</text>}
          </g>
        </g>
      )}
    </svg>
  );
}

function AssemblyView({ world }: { world: WorldState }) {
  const computers = world.orders_done;  // spending computers on upgrades must not lower this
  return (
    <div class="assembly">
      <p class="assembly-drone">{world.floor === "ASSEMBLY" ? "🤖 The drone is at the assembly bench." : "The drone is on another floor."}</p>
      <h3>Order #{world.orders_done + 1}</h3>
      <ul class="order">
        {Object.entries(world.order ?? {}).map(([part, need]) => {
          const have = world.inventory[part] ?? 0;
          return <li key={part} class={have >= need ? "ok" : ""}>{PART_ICON[part]} {part}: {have} / {need}</li>;
        })}
      </ul>
      <p class="computers">🖥️ Computers built: <strong>{computers}</strong> / {WIN_COMPUTERS}</p>
      {computers >= WIN_COMPUTERS && <p class="win">🏆 ByteWorks is back in business! Keep going for fun.</p>}
    </div>
  );
}
