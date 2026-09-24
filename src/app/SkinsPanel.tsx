import { useState } from "preact/hooks";
import type { BuyResult, SkinInfo, WorldState } from "../engine/types";
import { Drone, PartIcon } from "./art";

interface Props {
  skins: SkinInfo[]; world: WorldState; equipped: string; running: boolean;
  onBuy: (id: string) => Promise<BuyResult>; onEquip: (id: string) => void; onClose: () => void;
}

export function SkinsPanel({ skins, world, equipped, running, onBuy, onEquip, onClose }: Props) {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const owned = new Set(world.skins ?? ["classic"]);
  const canAfford = (s: SkinInfo) => Object.entries(s.cost).every(([p, n]) => (world.inventory[p] ?? 0) >= n);

  const buy = async (s: SkinInfo) => {
    setBusy(true);
    try {
      const result = await onBuy(s.id);
      setMessage(result.message);
      if (result.ok) onEquip(s.id);
    } catch (err) {
      setMessage(`Something went wrong: ${err}`);
    } finally {
      setBusy(false);
    }
  };

  return (
    <aside class="drawer panel" role="dialog" aria-label="Skins">
      <div class="drawer-head">
        <h2>🎨 Skins</h2>
        <button class="btn small" onClick={onClose}>Close</button>
      </div>
      <p class="skins-intro">Make your drone look the part. Skins are just for show, and wildly overpriced.</p>
      {message && <p class="upgrade-msg" role="status">{message}</p>}
      <ul class="skin-list">
        {skins.map((s) => {
          const have = owned.has(s.id);
          const wearing = equipped === s.id;
          return (
            <li key={s.id} class={`skin ${wearing ? "wearing" : ""}`}>
              <svg class="skin-preview" viewBox="0 0 100 100" aria-hidden="true"><Drone facing={0} stunned={false} skin={s.id} /></svg>
              <div class="skin-info">
                <div class="upgrade-title">{s.name}</div>
                <div class="upgrade-summary">{s.blurb}</div>
                {!have && (
                  <div class="upgrade-cost">
                    {Object.entries(s.cost).map(([p, n]) => (
                      <span key={p} class={`cost ${(world.inventory[p] ?? 0) >= n ? "ok" : ""}`}><PartIcon part={p} size={18} label={p} /> {n.toLocaleString()}</span>
                    ))}
                  </div>
                )}
                {wearing ? <span class="skin-wearing">✓ Equipped</span>
                  : have ? <button class="btn small" onClick={() => onEquip(s.id)}>Equip</button>
                  : <button class="btn small primary" disabled={running || busy || !canAfford(s)} onClick={() => buy(s)}>
                      {running ? "Stop program to buy" : canAfford(s) ? "Buy" : "Not enough parts"}
                    </button>}
              </div>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
