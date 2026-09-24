import { useRef } from "preact/hooks";
import type { WorldState } from "../engine/types";
import { WIN_COMPUTERS, type FloorInfo } from "../floors";
import { lookOf, moveDuration, nextHeading, svgRow, type DronePos } from "./floorMath";
import { Drone, PartArt, PartIcon, ScoreBadge } from "./art";

const CELL = 100;

interface Props { floor: FloorInfo; world: WorldState; animMs: number; locked: boolean; lockedBy: string }

export function FloorView({ floor, world, animMs, locked, lockedBy }: Props) {
  const prev = useRef<DronePos | null>(null);
  const heading = useRef(0);
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
  heading.current = nextHeading(prev.current, pos, heading.current);
  prev.current = pos;

  return (
    <svg class="floor-svg" viewBox={`0 0 ${n * CELL} ${n * CELL}`} role="img" aria-label={`${floor.name}: ${n} by ${n} grid`}
      style={{ "--floor": floor.color }}>
      {state.grid.map((column, x) => column.map((tile, y) => {
        const look = lookOf(tile, world.clock);
        return (
          <g key={`${x}-${y}`} transform={`translate(${x * CELL} ${svgRow(y, n) * CELL})`}>
            <rect x="3" y="3" width="94" height="94" rx="9" class={`tile${look.ready ? " ready" : ""}${look.faulty ? " faulty" : ""}`} />
            <g class="tile-bolts">
              <circle cx="11" cy="11" r="1.6" /><circle cx="89" cy="11" r="1.6" /><circle cx="11" cy="89" r="1.6" /><circle cx="89" cy="89" r="1.6" />
            </g>
            {look.part && <PartArt part={look.part} faulty={look.faulty} ready={look.ready} />}
            {look.part && !look.ready && (
              <g>
                <rect x="16" y="85" width="68" height="4" rx="2" class="grow-track" />
                <rect x="16" y="85" width={68 * look.progress} height="4" rx="2" class="grow-bar" />
              </g>
            )}
            {look.score !== null && <ScoreBadge score={look.score} />}
          </g>
        );
      }))}
      {world.floor === floor.id && (
        <g class="drone" style={{ transform: `translate(${world.x * CELL}px, ${svgRow(world.y, n) * CELL}px)`, transitionDuration: `${duration}ms` }}>
          <Drone facing={heading.current} stunned={!!world.bumped} />
        </g>
      )}
    </svg>
  );
}

function AssemblyView({ world }: { world: WorldState }) {
  const computers = world.orders_done;  // spending computers on upgrades must not lower this
  return (
    <div class="assembly">
      {world.floor === "ASSEMBLY" && <p class="assembly-drone">The drone is at the assembly bench.</p>}
      <h3>Order #{world.orders_done + 1}</h3>
      <ul class="order">
        {Object.entries(world.order ?? {}).map(([part, need]) => {
          const have = world.inventory[part] ?? 0;
          return <li key={part} class={have >= need ? "ok" : ""}><PartIcon part={part} size={26} /> {part}: {have} / {need}</li>;
        })}
      </ul>
      <p class="computers"><PartIcon part="COMPUTER" size={30} /> Computers built: <strong>{computers}</strong> / {WIN_COMPUTERS}</p>
      {computers >= WIN_COMPUTERS && <p class="win">🏆 ByteWorks is back in business! Keep going for fun.</p>}
    </div>
  );
}
