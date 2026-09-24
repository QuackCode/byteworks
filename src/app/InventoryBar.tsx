import type { WorldState } from "../engine/types";
import { FLOORS, PARTS_ORDER, PART_ICON } from "../floors";

const UNLOCK_FOR_PART: Record<string, string | null> = {
  ...Object.fromEntries(FLOORS.map((f) => [f.id, f.unlock])), COMPUTER: "floor_assembly",
};

export function InventoryBar({ world }: { world: WorldState | null }) {
  if (!world) return <div class="inventory">Starting…</div>;
  const owned = new Set(world.unlocks);
  const shown = PARTS_ORDER.filter((p) => !UNLOCK_FOR_PART[p] || owned.has(UNLOCK_FOR_PART[p]!) || (world.inventory[p] ?? 0) > 0);
  return (
    <div class="inventory" aria-label="Parts you have">
      {shown.map((p) => (
        <span class="inv" key={p} title={p}>{PART_ICON[p]} <b>{(world.inventory[p] ?? 0).toLocaleString()}</b></span>
      ))}
    </div>
  );
}
