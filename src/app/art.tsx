// Hand-drawn SVG art for the factory: computer parts (top-down) and the drone.
// Everything is drawn in a 100 x 100 box centred on (50, 50). Shared gradients and
// filters live in <ArtDefs/>, which App renders once so every SVG on the page can use them.
import { memo } from "preact/compat";

export function ArtDefs() {
  return (
    <svg class="art-defs" width="0" height="0" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="g-pcb" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#2f9a5f" /><stop offset="1" stop-color="#1b6a3f" />
        </linearGradient>
        <linearGradient id="g-pcb-dark" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#2b313c" /><stop offset="1" stop-color="#161a21" />
        </linearGradient>
        <linearGradient id="g-board" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#23806f" /><stop offset="1" stop-color="#134a41" />
        </linearGradient>
        <linearGradient id="g-gold" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#ffe29a" /><stop offset="1" stop-color="#c8922b" />
        </linearGradient>
        <linearGradient id="g-silver" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#f1f4f8" /><stop offset="0.55" stop-color="#b7bfca" /><stop offset="1" stop-color="#8b94a1" />
        </linearGradient>
        <linearGradient id="g-chip" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#383d47" /><stop offset="1" stop-color="#15181d" />
        </linearGradient>
        <linearGradient id="g-shroud" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#474d59" /><stop offset="1" stop-color="#1c1f26" />
        </linearGradient>
        <linearGradient id="g-gunmetal" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#5a6477" /><stop offset="1" stop-color="#262c38" />
        </linearGradient>
        <linearGradient id="g-amber" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#ffd36b" /><stop offset="1" stop-color="#d98f12" />
        </linearGradient>
        <linearGradient id="g-plate" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#2a303c" /><stop offset="1" stop-color="#1c2029" />
        </linearGradient>
        <radialGradient id="g-scorch">
          <stop offset="0" stop-color="#120804" stop-opacity="0.95" />
          <stop offset="0.6" stop-color="#3a1a0a" stop-opacity="0.6" />
          <stop offset="1" stop-color="#3a1a0a" stop-opacity="0" />
        </radialGradient>
        <radialGradient id="g-rotor">
          <stop offset="0" stop-color="#cfe6ff" stop-opacity="0.05" />
          <stop offset="1" stop-color="#cfe6ff" stop-opacity="0.22" />
        </radialGradient>
        <filter id="f-glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="1.6" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="f-shadow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="3" />
        </filter>
        {/* Parts still being built show as a see-through cyan blueprint */}
        <filter id="f-blueprint">
          <feColorMatrix type="matrix" values="0.1 0.2 0.05 0 0.05  0.25 0.5 0.15 0 0.2  0.3 0.6 0.2 0 0.35  0 0 0 0.55 0" />
        </filter>
      </defs>
    </svg>
  );
}

function RamStick() {
  const fingers = [];
  for (let x = 15; x <= 84; x += 3) if (x < 46 || x > 51) fingers.push(<rect key={x} x={x} y="59" width="1.8" height="5" fill="url(#g-gold)" />);
  return (
    <g>
      <path d="M12 36h76v28h-38v-2h-3v2H12z" fill="url(#g-pcb)" stroke="#0f4a2a" stroke-width="0.8" />
      {[16, 33, 55, 72].map((x) => (
        <g key={x}>
          <rect x={x} y="40" width="13" height="13" rx="1" fill="url(#g-chip)" />
          <rect x={x + 1.5} y="41.5" width="10" height="1.2" fill="#ffffff" opacity="0.12" />
        </g>
      ))}
      <rect x="47.5" y="42" width="5" height="9" rx="0.8" fill="#d9d2b8" opacity="0.8" />
      {fingers}
    </g>
  );
}

function CpuChip() {
  const caps = [];
  for (let i = 0; i < 6; i++) {
    caps.push(<rect key={`t${i}`} x={29 + i * 7.5} y="24.5" width="3" height="1.6" fill="#a86b3c" />);
    caps.push(<rect key={`b${i}`} x={29 + i * 7.5} y="73.9" width="3" height="1.6" fill="#a86b3c" />);
  }
  return (
    <g>
      <rect x="22" y="22" width="56" height="56" rx="4" fill="url(#g-pcb)" stroke="#0f4a2a" stroke-width="0.8" />
      {caps}
      <rect x="29" y="29" width="42" height="42" rx="5" fill="url(#g-silver)" stroke="#7d8591" stroke-width="0.8" />
      <rect x="32" y="32" width="36" height="36" rx="3.5" fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="0.8" />
      <text x="50" y="49" text-anchor="middle" class="art-engrave">BYTE</text>
      <text x="50" y="57" text-anchor="middle" class="art-engrave small">CORE X9</text>
      <path d="M22 30 L22 22 L30 22 Z" fill="url(#g-gold)" />
    </g>
  );
}

function Ssd() {
  return (
    <g>
      <path d="M17 39h67a4 4 0 0 1 4 4v1.5a3 3 0 0 0 0 11V57a4 4 0 0 1-4 4H17z" fill="url(#g-pcb-dark)" stroke="#07090c" stroke-width="0.8" />
      {[0, 1, 2, 3, 4, 5].map((i) => <rect key={i} x="12" y={40.5 + i * 3.3} width="5.5" height="2" fill="url(#g-gold)" />)}
      <rect x="12" y="47.5" width="5.5" height="1.6" fill="#161a21" />
      <rect x="21" y="42" width="15" height="16" rx="1" fill="url(#g-chip)" />
      <rect x="39" y="42" width="15" height="16" rx="1" fill="url(#g-chip)" />
      <rect x="57" y="44" width="10" height="12" rx="1" fill="#2f343d" stroke="#4a505c" stroke-width="0.5" />
      <rect x="21" y="42" width="33" height="16" rx="1" fill="#eef0f3" opacity="0.9" />
      <rect x="21" y="42" width="33" height="4" rx="1" fill="#b18cff" />
      <text x="37.5" y="54.5" text-anchor="middle" class="art-label">1TB NVMe</text>
    </g>
  );
}

function Motherboard({ faulty }: { faulty: boolean }) {
  const pins = [];
  for (let r = 0; r < 5; r++) for (let c = 0; c < 5; c++) pins.push(<circle key={`${r}${c}`} cx={32 + c * 3.5} cy={32 + r * 3.5} r="0.8" fill="#c9a24a" />);
  return (
    <g>
      <rect x="15" y="15" width="70" height="70" rx="3" fill="url(#g-board)" stroke="#0b332c" stroke-width="0.8" />
      <path d="M20 60h14l6-6h14M20 66h22l4 4h26M58 20v10l-4 4v10M40 78h12l6-6" fill="none" stroke="#5fd4bd" stroke-opacity="0.35" stroke-width="0.9" />
      <rect x="15" y="22" width="6" height="26" fill="#9aa3af" />
      <rect x="28" y="28" width="22" height="22" rx="1.5" fill="#d7dbe1" stroke="#8f98a4" stroke-width="0.7" />
      <rect x="30" y="30" width="18" height="18" fill="#3a3f48" />
      {pins}
      {[62, 67].map((x) => (
        <g key={x}>
          <rect x={x} y="20" width="3.2" height="42" fill="#15181d" />
          <rect x={x - 0.4} y="20" width="4" height="3" fill="#e8e8e8" />
          <rect x={x - 0.4} y="59" width="4" height="3" fill="#e8e8e8" />
        </g>
      ))}
      <rect x="22" y="72" width="50" height="3.5" rx="0.8" fill="#15181d" />
      <rect x="25" y="72.8" width="44" height="1.8" fill="url(#g-gold)" opacity="0.8" />
      {[[55, 30], [55, 37], [55, 44], [24, 55], [31, 55]].map(([x, y]) => (
        <g key={`${x}${y}`}>
          <circle cx={x} cy={y} r="2.6" fill="url(#g-silver)" />
          <path d={`M${x - 1.6} ${y}h3.2M${x} ${y - 1.6}v3.2`} stroke="#6b7380" stroke-width="0.6" />
        </g>
      ))}
      <circle cx="76" cy="76" r="3" fill="#d9d2b8" stroke="#7a755e" stroke-width="0.5" />
      {faulty && (
        <g class="art-fault">
          <circle cx="39" cy="39" r="22" fill="url(#g-scorch)" />
          <path d="M31 44l5-4 2 3 6-6" fill="none" stroke="#ff7a2e" stroke-width="1.4" filter="url(#f-glow)" />
          <g class="art-smoke">
            <circle cx="37" cy="30" r="4" fill="#9aa0a8" opacity="0.5" />
            <circle cx="43" cy="24" r="5" fill="#9aa0a8" opacity="0.35" />
            <circle cx="36" cy="18" r="6" fill="#9aa0a8" opacity="0.2" />
          </g>
          <path d="M74 19l8 14h-16z" fill="#ff5d5d" stroke="#2a0b0b" stroke-width="0.8" />
          <rect x="73.3" y="23.5" width="1.4" height="5" fill="#2a0b0b" />
          <circle cx="74" cy="30.5" r="0.8" fill="#2a0b0b" />
        </g>
      )}
    </g>
  );
}

const BLADE = "M0 -2.4 C3.5 -4.5 6.5 -7.5 7.2 -10.8 C4 -10.4 1 -8 -1.2 -3.4 Z";

function Fan({ cx, spin }: { cx: number; spin: boolean }) {
  return (
    <g transform={`translate(${cx} 50)`}>
      <circle r="14" fill="#101216" stroke="#5b6270" stroke-width="1" />
      <g class={spin ? "art-fan spin" : "art-fan"}>
        {[0, 1, 2, 3, 4, 5, 6].map((i) => <path key={i} d={BLADE} transform={`rotate(${i * 51.4})`} fill="#3b414c" stroke="#666e7b" stroke-width="0.4" />)}
      </g>
      <circle r="4.2" fill="#262a31" stroke="#ff7a59" stroke-width="0.8" />
    </g>
  );
}

function Gpu({ ready }: { ready: boolean }) {
  return (
    <g>
      {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => <rect key={i} x={22 + i * 3.4} y="70" width="2" height="4" fill="url(#g-gold)" />)}
      <path d="M11 32h72l6 6v26l-6 6H11z" fill="url(#g-shroud)" stroke="#0c0e12" stroke-width="0.8" />
      <path d="M11 32h30l-6 5H11zM89 44v10l-3 3V47z" fill="#ff7a59" opacity="0.9" />
      <path d="M47 36l4 28" stroke="#ffffff" stroke-opacity="0.08" stroke-width="3" />
      <Fan cx={31} spin={ready} />
      <Fan cx={67} spin={ready} />
    </g>
  );
}

function Computer() {
  return (
    <g>
      <rect x="28" y="14" width="44" height="72" rx="4" fill="url(#g-shroud)" stroke="#0c0e12" stroke-width="0.8" />
      <rect x="33" y="19" width="30" height="62" rx="2.5" fill="#0d1220" stroke="#5aa9ff" stroke-opacity="0.6" stroke-width="0.8" />
      {[31, 50].map((y) => (
        <g key={y}>
          <circle cx="48" cy={y} r="7.5" fill="none" stroke="#ff5c8a" stroke-width="1.6" filter="url(#f-glow)" />
          <circle cx="48" cy={y} r="2" fill="#2a2f38" />
        </g>
      ))}
      <rect x="37" y="63" width="22" height="10" rx="1" fill="url(#g-shroud)" stroke="#5aa9ff" stroke-opacity="0.5" stroke-width="0.6" />
      <rect x="66" y="20" width="3" height="3" rx="1.5" fill="#6dff8a" filter="url(#f-glow)" />
    </g>
  );
}

interface PartProps { part: string; faulty?: boolean; ready?: boolean }

/** A part as an SVG group (for use inside another SVG). */
export const PartArt = memo(function PartArt({ part, faulty = false, ready = true }: PartProps) {
  const art = part === "RAM" ? <g transform="translate(50 50) scale(1.1 1.2) translate(-50 -50)"><RamStick /></g> : part === "CPU" ? <CpuChip /> : part === "SSD" ? <g transform="translate(50 50) scale(1.14 1.3) translate(-50 -50)"><Ssd /></g>
    : part === "BOARD" ? <Motherboard faulty={faulty} /> : part === "GPU" ? <Gpu ready={ready} /> : <Computer />;
  return <g filter={ready ? undefined : "url(#f-blueprint)"}>{art}</g>;
});

// Snug frame around each part's drawing, so long parts (RAM, SSD) aren't tiny in icons
const ICON_BOX: Record<string, [number, number, number, number]> = {
  RAM: [10, 30, 80, 40], SSD: [10, 30, 80, 40], CPU: [20, 20, 60, 60], BOARD: [13, 13, 74, 74],
  GPU: [9, 29, 82, 47], COMPUTER: [25, 12, 50, 76],
};

/** A part as a small standalone icon (inventory, orders, upgrade costs, floor names). `size` is the height. */
export function PartIcon({ part, size = 22, label }: { part: string; size?: number; label?: string }) {
  const [x, y, w, h] = ICON_BOX[part] ?? [8, 8, 84, 84];
  return (
    <svg class="part-icon" width={Math.round((size * w) / h)} height={size} viewBox={`${x} ${y} ${w} ${h}`}
      role={label ? "img" : undefined} aria-label={label} aria-hidden={label ? undefined : "true"}>
      <PartArt part={part} />
    </svg>
  );
}

/** GPU benchmark score on a little LED panel: red for low scores, green for high. */
export function ScoreBadge({ score }: { score: number }) {
  const hue = Math.round((score / 9) * 120);
  return (
    <g transform="translate(70 8)">
      <rect width="22" height="16" rx="3" fill="#07090c" stroke="#3a4152" stroke-width="1" />
      <text x="11" y="12.5" text-anchor="middle" class="art-score" fill={`hsl(${hue} 90% 60%)`} filter="url(#f-glow)">{score}</text>
    </g>
  );
}

/** The factory drone, seen from above. `facing` is degrees clockwise from North. */
export function Drone({ facing, stunned }: { facing: number; stunned: boolean }) {
  const eye = stunned ? "#ff4d4d" : "#5ce1ff";
  const rotors: [number, number][] = [[24, 24], [76, 24], [24, 76], [76, 76]];
  return (
    <g class={stunned ? "drone-art stunned" : "drone-art"}>
      <ellipse cx="50" cy="60" rx="30" ry="11" fill="#000" opacity="0.45" filter="url(#f-shadow)" />
      <g class="drone-hover">
        <g class="drone-heading" style={{ transform: `rotate(${facing}deg)` }}>
          {rotors.map(([x, y]) => <line key={`a${x}${y}`} x1="50" y1="50" x2={x} y2={y} stroke="url(#g-gunmetal)" stroke-width="6" stroke-linecap="round" />)}
          {rotors.map(([x, y]) => (
            <g key={`r${x}${y}`} transform={`translate(${x} ${y})`}>
              <circle r="14" fill="url(#g-rotor)" stroke="#c6dcf5" stroke-opacity="0.6" stroke-width="1.4" />
              <g class="drone-rotor">
                <rect x="-13" y="-1.4" width="26" height="2.8" rx="1.4" fill="#d6dde7" opacity="0.8" />
                <rect x="-1.4" y="-13" width="2.8" height="26" rx="1.4" fill="#d6dde7" opacity="0.35" />
              </g>
              <circle r="3.4" fill="#2b313c" stroke="#8e98a8" stroke-width="0.8" />
            </g>
          ))}
          {/* grabber claws point the way the drone is flying */}
          <path d="M43 26l-4-8 5-4M57 26l4-8-5-4" fill="none" stroke="#aab4c4" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M35 32l7-8h16l7 8v26l-7 10H42l-7-10z" fill="url(#g-gunmetal)" stroke="#12151b" stroke-width="1.4" />
          <path d="M39 39l5-5h12l5 5v17l-5 6H44l-5-6z" fill="url(#g-amber)" stroke="#8a5a00" stroke-width="0.8" />
          <path d="M44 47h12M44 51h12M44 55h12" stroke="#7a4f00" stroke-width="1.3" stroke-linecap="round" />
          <circle cx="50" cy="31" r="7" fill="#0b0e13" stroke="#aab4c4" stroke-width="1.2" />
          <circle cx="50" cy="31" r="3.6" fill={eye} filter="url(#f-glow)" class="drone-eye" />
          <circle cx="48.6" cy="29.6" r="1" fill="#ffffff" opacity="0.8" />
          <circle cx="44" cy="64" r="1.4" fill="#6dff8a" filter="url(#f-glow)" />
          <circle cx="56" cy="64" r="1.4" fill={stunned ? "#ff4d4d" : "#6dff8a"} filter="url(#f-glow)" />
        </g>
      </g>
      {stunned && (
        <g class="drone-stars">
          <animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="1s" repeatCount="indefinite" />
          {[0, 120, 240].map((a) => (
            <path key={a} transform={`rotate(${a} 50 50) translate(50 14)`} d="M0 -5l1.5 3.4 3.7.4-2.8 2.5.8 3.7L0 3.1-3.2 5l.8-3.7-2.8-2.5 3.7-.4z" fill="#ffd84d" stroke="#7a5a00" stroke-width="0.5" />
          ))}
        </g>
      )}
    </g>
  );
}
