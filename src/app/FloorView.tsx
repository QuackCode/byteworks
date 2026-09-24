import { useEffect, useRef, useState } from "preact/hooks";
import type { Floor } from "../floors";
import type { Level } from "../levels";
import type { FactoryEvent } from "../engine/events";

interface Props {
  floor: Floor;
  days: Level[];
  completed: number[];
  unlockedDays: number[];
  currentDay: number;
  locked: boolean;
  lockedHint: string;
  events: FactoryEvent[];
  runId: number;
  onSelectDay: (day: number) => void;
  /** Final Assembly only: which part floors are finished and sending parts upstairs */
  incoming?: { icon: string; name: string; ready: boolean }[];
}

type Result = "ship" | "reject" | "crash";
interface MovingPart {
  id: number;
  label: string;
  result: Result;
  start: number;
}

const PART_MS = 2600;
const GAP_MS = 520;
const MAX_PARTS = 14;
const BELT_Y = 226;
const BELT_START = 50;
const BELT_END = 790;

// Where a part is (and how it looks) t = 0..1 through its trip.
function place(result: Result, t: number) {
  const travel = result === "crash" ? 0.45 : 0.72;
  if (t < travel) {
    const end = result === "crash" ? 430 : BELT_END;
    return { x: BELT_START + (end - BELT_START) * (t / travel), y: BELT_Y, opacity: 1, boom: false };
  }
  const k = (t - travel) / (1 - travel);
  if (result === "ship") return { x: BELT_END + 115 * k, y: BELT_Y - 8 * k, opacity: 1 - k * 0.9, boom: false };
  if (result === "reject") return { x: BELT_END - 30 * k, y: BELT_Y + 60 * k, opacity: 1 - k * 0.7, boom: false };
  return { x: 430, y: BELT_Y, opacity: 1 - k, boom: true };
}

export function FloorView(p: Props) {
  const [parts, setParts] = useState<MovingPart[]>([]);
  const [now, setNow] = useState(() => performance.now());
  const [display, setDisplay] = useState<string | null>(null);
  const [poweredByRun, setPoweredByRun] = useState(false);
  const nextId = useRef(1);
  const partsRef = useRef(parts);
  partsRef.current = parts;

  const anyDone = p.days.some((d) => p.completed.includes(d.day));
  const floorDone = p.days.length > 0 && p.days.every((d) => p.completed.includes(d.day));
  // The Control Room stays dark until the main power is switched on (Day 1).
  const lit = !p.locked && (p.floor.id !== 0 || anyDone || poweredByRun);

  // Replay the latest run's events on this floor
  useEffect(() => {
    setPoweredByRun(false);
    setDisplay(null);
    if (!p.runId) return;
    const t0 = performance.now();
    const queued: MovingPart[] = [];
    for (const ev of p.events) {
      if (ev.type === "power_on") setPoweredByRun(true);
      else if (ev.type === "display") setDisplay(ev.text);
      else if (ev.type === "part" && queued.length < MAX_PARTS) {
        queued.push({ id: nextId.current++, label: ev.label, result: ev.result, start: t0 + queued.length * GAP_MS });
      }
    }
    setParts(queued);
  }, [p.runId]);

  useEffect(() => {
    setParts([]);
    setDisplay(null);
  }, [p.floor.id]);

  // Animation loop. Finished floors keep producing parts on their own.
  useEffect(() => {
    let raf = 0;
    let lastIdle = 0;
    const reduceMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    const tick = (time: number) => {
      // Only re-render while something is moving
      if (partsRef.current.length || floorDone) setNow(time);
      if (!partsRef.current.length && !floorDone) {
        raf = requestAnimationFrame(tick);
        return;
      }
      setParts((cur) => {
        let next = cur.filter((part) => time - part.start < PART_MS);
        if (floorDone && !reduceMotion && time - lastIdle > 1500 && next.every((x) => x.label === "")) {
          lastIdle = time;
          next = [...next, { id: nextId.current++, label: "", result: "ship", start: time }];
        }
        return next.length === cur.length && next.every((x, i) => x === cur[i]) ? cur : next;
      });
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [floorDone, p.floor.id]);

  const slots = p.days.length;
  const slotW = Math.min(170, 700 / Math.max(slots, 1));
  const color = p.floor.color;
  const beltMoving = lit && (parts.length > 0 || floorDone);

  return (
    <svg class="floor-svg" viewBox="0 0 1000 320" role="img"
      aria-label={`${p.floor.name}${p.locked ? " (locked)" : ""}`} style={{ "--floor": color }}>
      <defs>
        {["belt", "belt-moving"].map((id) => (
          <pattern key={id} id={id} width="24" height="26" patternUnits="userSpaceOnUse">
            {id === "belt-moving" && <animate attributeName="x" from="0" to="24" dur="0.5s" repeatCount="indefinite" />}
            <rect width="24" height="26" fill="var(--belt)" />
            <rect x="0" width="4" height="26" fill="var(--belt-line)" />
          </pattern>
        ))}
        <linearGradient id="wall" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stop-color="var(--wall-top)" />
          <stop offset="1" stop-color="var(--wall-bottom)" />
        </linearGradient>
      </defs>

      <rect width="1000" height="320" fill="url(#wall)" />
      <rect y="262" width="1000" height="58" fill="var(--ground)" />
      <rect y="258" width="1000" height="4" fill={color} opacity="0.6" />

      {/* Floor sign */}
      <g transform="translate(24 22)">
        <rect width="250" height="46" rx="8" fill="var(--sign)" stroke={color} stroke-width="2" />
        <text x="14" y="30" class="floor-sign">{p.floor.icon} {p.floor.label} · {p.floor.name}</text>
      </g>

      {/* Wall screen */}
      <g transform="translate(700 20)">
        <rect width="276" height="52" rx="6" fill="var(--screen)" stroke="var(--screen-edge)" stroke-width="3" />
        <text x="138" y="33" text-anchor="middle" class={`screen-text ${lit ? "on" : ""}`}>
          {!lit ? (p.locked ? "LOCKED" : "NO POWER") : display ?? (floorDone ? `${p.floor.part}: RUNNING` : `${p.floor.part}`)}
        </text>
      </g>

      {/* Machines, one per day on this floor */}
      {p.days.map((d, i) => {
        const x = 40 + i * (slotW + 14);
        const done = p.completed.includes(d.day);
        const open = p.unlockedDays.includes(d.day);
        const current = d.day === p.currentDay;
        return (
          <g key={d.day} class={`machine ${done ? "done" : open ? "open" : "locked"} ${current ? "current" : ""}`}
            transform={`translate(${x} 92)`} onClick={() => open && p.onSelectDay(d.day)}
            role="button" tabIndex={open ? 0 : -1} aria-label={`Day ${d.day}: ${d.machine}${done ? " (built)" : open ? "" : " (locked)"}`}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && open && p.onSelectDay(d.day)}>
            <rect width={slotW} height="92" rx="8" class="machine-body" />
            {done && <rect width={slotW} height="8" rx="4" fill={color} />}
            <text x={slotW / 2} y="30" text-anchor="middle" class="machine-day">Day {d.day}</text>
            <text x={slotW / 2} y="52" text-anchor="middle" class="machine-name">
              {d.machine.length > 18 ? d.machine.slice(0, 17) + "…" : d.machine}
            </text>
            <text x={slotW / 2} y="76" text-anchor="middle" class="machine-state">
              {done ? "✓ built" : open ? "▶ build me" : "🔒"}
            </text>
            <rect x={slotW / 2 - 4} y="92" width="8" height="30" fill="var(--pipe)" />
          </g>
        );
      })}

      {/* Final Assembly: parts arriving by lift from the floors below */}
      {p.incoming && (
        <g transform="translate(480 92)">
          <text x="0" y="-8" class="machine-day">PARTS ARRIVING BY LIFT</text>
          {p.incoming.map((f, i) => (
            <g key={f.name} transform={`translate(${i * 96} 0)`} opacity={f.ready ? 1 : 0.35}>
              <rect width="86" height="84" rx="8" class="machine-body" />
              <text x="43" y="36" text-anchor="middle" font-size="26">{f.icon}</text>
              <text x="43" y="60" text-anchor="middle" class="machine-state">{f.name}</text>
              <text x="43" y="76" text-anchor="middle" class="machine-day">{f.ready ? "✓ ready" : "waiting"}</text>
            </g>
          ))}
        </g>
      )}

      {/* Conveyor belt */}
      <rect x={BELT_START - 14} y={BELT_Y - 13} width={BELT_END - BELT_START + 34} height="26" rx="13"
        fill={beltMoving ? "url(#belt-moving)" : "url(#belt)"} />

      {/* Bins */}
      <g transform="translate(870 176)">
        <rect width="110" height="80" rx="8" fill="var(--bin-ok)" />
        <text x="55" y="34" text-anchor="middle" class="bin-text">SHIPPED</text>
        <text x="55" y="56" text-anchor="middle" class="bin-sub">{p.floor.id < 7 ? "↑ upstairs" : "to customers"}</text>
      </g>
      <g transform="translate(700 270)">
        <rect width="110" height="44" rx="8" fill="var(--bin-bad)" />
        <text x="55" y="28" text-anchor="middle" class="bin-text">REJECT</text>
      </g>

      {/* Moving parts */}
      {parts.map((part) => {
        const t = Math.max(0, (now - part.start) / PART_MS);
        if (now < part.start) return null;
        const pos = place(part.result, t);
        const bad = part.result !== "ship" && t > 0.4;
        return (
          <g key={part.id} transform={`translate(${pos.x} ${pos.y})`} opacity={pos.opacity}>
            {pos.boom ? (
              <text x="0" y="12" text-anchor="middle" font-size="44">💥</text>
            ) : (
              <>
                <rect x="-38" y="-12" width="76" height="24" rx="5" fill={bad ? "var(--bad)" : color} stroke="#0008" />
                <text y="4" text-anchor="middle" class="part-label">{part.label || p.floor.icon}</text>
              </>
            )}
          </g>
        );
      })}

      {/* Lights off / locked overlay */}
      {!lit && <rect width="1000" height="320" fill="#000" opacity={p.locked ? 0.72 : 0.55} class="darkness" />}
      {p.locked && (
        <text x="500" y="170" text-anchor="middle" class="locked-text">🔒 {p.lockedHint}</text>
      )}
    </svg>
  );
}
