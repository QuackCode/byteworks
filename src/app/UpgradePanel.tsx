import { useState } from "preact/hooks";
import type { BuyResult, UnlockInfo, WorldState } from "../engine/types";
import { PART_ICON } from "../floors";

interface Props {
  tree: UnlockInfo[]; world: WorldState; running: boolean;
  onBuy: (id: string) => Promise<BuyResult>; onHelp: (helpId: string) => void; onClose: () => void;
}

export function UpgradePanel({ tree, world, running, onBuy, onHelp, onClose }: Props) {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const owned = new Set(world.unlocks);
  const canAfford = (u: UnlockInfo) => Object.entries(u.cost).every(([p, n]) => (world.inventory[p] ?? 0) >= n);
  const ready = tree.filter((u) => !owned.has(u.id) && u.requires.every((r) => owned.has(r)));
  const readyIds = new Set(ready.map((u) => u.id));
  // One step ahead only: items whose missing requirements are all buyable right now
  const next = tree.filter((u) => !owned.has(u.id) && !readyIds.has(u.id)
    && u.requires.every((r) => owned.has(r) || readyIds.has(r)));
  const done = tree.filter((u) => owned.has(u.id));
  const titleOf = (id: string) => tree.find((u) => u.id === id)?.title ?? id;

  const buy = async (u: UnlockInfo) => {
    setBusy(true);
    try {
      setMessage((await onBuy(u.id)).message);
    } catch (err) {
      setMessage(`Something went wrong: ${err}`);
    } finally {
      setBusy(false);
    }
  };

  const card = (u: UnlockInfo, state: "ready" | "next" | "done") => (
    <li key={u.id} class={`upgrade ${state} kind-${u.kind}`}>
      <div class="upgrade-title">{u.title}</div>
      <div class="upgrade-summary">{u.summary}</div>
      <div class="upgrade-cost">
        {Object.entries(u.cost).map(([p, n]) => (
          <span key={p} class={`cost ${(world.inventory[p] ?? 0) >= n ? "ok" : ""}`}>{PART_ICON[p]} {n}</span>
        ))}
      </div>
      {state === "ready" && (
        <button class="btn small primary" disabled={running || busy || !canAfford(u)} onClick={() => buy(u)}>
          {running ? "Stop program to buy" : canAfford(u) ? "Buy" : "Not enough parts"}
        </button>
      )}
      {state === "next" && <div class="upgrade-needs">Needs {u.requires.filter((r) => !owned.has(r)).map(titleOf).join(", ")}</div>}
      {state === "done" && u.help && <button class="btn small ghost" onClick={() => onHelp(u.help!)}>📖 Help</button>}
    </li>
  );

  return (
    <aside class="drawer panel" role="dialog" aria-label="Upgrades">
      <div class="drawer-head">
        <h2>⬆️ Upgrades</h2>
        <button class="btn small" onClick={onClose}>Close</button>
      </div>
      {message && <p class="upgrade-msg" role="status">{message}</p>}
      <h3>Available</h3>
      <ul class="upgrade-list">{ready.length ? ready.map((u) => card(u, "ready")) : <li class="empty">Nothing right now: keep harvesting!</li>}</ul>
      {next.length > 0 && <><h3>Coming up</h3><ul class="upgrade-list">{next.map((u) => card(u, "next"))}</ul></>}
      {done.length > 0 && <details><summary>Owned ({done.length})</summary><ul class="upgrade-list">{done.map((u) => card(u, "done"))}</ul></details>}
    </aside>
  );
}
