import { useEffect, useRef, useState } from "preact/hooks";
import { game } from "../engine/game";
import type { RunnerStatus, UnlockInfo, WorldState } from "../engine/types";
import { emptySave, loadSave, storeSave, type Save } from "../engine/save";
import { FLOORS } from "../floors";
import { FloorView } from "./FloorView";
import { InventoryBar } from "./InventoryBar";
import { CodePanel, type ConsoleLine } from "./CodePanel";
import { SaveDialog } from "./SaveDialog";

const AUTOSAVE_MS = 5000;
const MAX_LINES = 300;

function isTyping(el: EventTarget | null) {
  return !!(el as HTMLElement | null)?.closest?.(".cm-editor, input, textarea, [contenteditable]");
}

export function App() {
  const [save, setSave] = useState<Save>(loadSave);
  const saveRef = useRef(save);
  const [world, setWorld] = useState<WorldState | null>(save.world);
  const [animMs, setAnimMs] = useState(0);
  const [status, setStatus] = useState<RunnerStatus>("loading");
  const [running, setRunning] = useState(false);
  const [tree, setTree] = useState<UnlockInfo[]>([]);
  const [lines, setLines] = useState<ConsoleLine[]>([]);
  const [viewFloor, setViewFloor] = useState(save.world?.floor ?? "RAM");
  const [panel, setPanel] = useState<"none" | "upgrades" | "help" | "save">(save.world ? "none" : "help");
  const [helpId, setHelpId] = useState("start");
  const [editKey, setEditKey] = useState(0);

  const persist = (patch: Partial<Save>) => {
    const next = { ...saveRef.current, ...patch };
    saveRef.current = next;
    setSave(next);
    storeSave(next);
  };
  const addLine = (text: string, kind: ConsoleLine["kind"]) => setLines((cur) => [...cur.slice(-(MAX_LINES - 1)), { text, kind }]);

  useEffect(() => {
    game.onStatus = setStatus;
    game.onState = (state, ms) => { setWorld(state); setAnimMs(ms); };
    game.onPrint = (text) => addLine(text, "out");
    game.setSpeed(save.settings.speed);
    game.start(save.world);
    game.tree().then(setTree).catch(() => addLine("Couldn't load the upgrade tree. Refresh the page.", "err"));
    const timer = setInterval(() => { if (game.running && game.latest) persist({ world: game.latest }); }, AUTOSAVE_MS);
    return () => clearInterval(timer);
  }, []);

  // Camera follows the drone between floors (unless the player turned that off)
  useEffect(() => {
    if (save.settings.follow && world) setViewFloor(world.floor);
  }, [world?.floor, save.settings.follow]);

  const owned = new Set(world?.unlocks ?? []);
  const floorIndex = Math.max(0, FLOORS.findIndex((f) => f.id === viewFloor));
  const floor = FLOORS[floorIndex];
  const lockedBy = tree.find((u) => u.id === floor.unlock)?.title ?? "an upgrade";
  const windows = 1 + tree.filter((u) => owned.has(u.id)).reduce((sum, u) => sum + u.windows, 0);
  const affordable = world ? tree.filter((u) => !owned.has(u.id) && u.requires.every((r) => owned.has(r))
    && Object.entries(u.cost).every(([p, n]) => (world.inventory[p] ?? 0) >= n)).length : 0;

  const indexRef = useRef(floorIndex);
  indexRef.current = floorIndex;
  const goFloor = (index: number) => {
    if (index < 0 || index >= FLOORS.length) return;
    indexRef.current = index;
    setViewFloor(FLOORS[index].id);
  };
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (isTyping(e.target) || panel !== "none") return;
      if (e.key === "ArrowUp") { e.preventDefault(); goFloor(indexRef.current + 1); }
      if (e.key === "ArrowDown") { e.preventDefault(); goFloor(indexRef.current - 1); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [panel]);

  const onRun = async () => {
    if (running || status !== "ready") return;
    const { files, active } = saveRef.current;
    setRunning(true);
    addLine(`▶ Running ${active}`, "info");
    try {
      const result = await game.run(files, active);
      if (result.error) result.error.split("\n").forEach((l) => addLine(l, "err"));
      else addLine(result.stopped ? "■ Stopped" : "✓ Program finished", "info");
      persist({ world: result.state });
    } catch (err) {
      addLine(`Something went wrong: ${err}`, "err");
    } finally {
      setRunning(false);
    }
  };

  const onBuy = async (id: string) => {
    const result = await game.buy(id);
    persist({ world: result.state });
    const unlock = tree.find((u) => u.id === id);
    if (result.ok && unlock?.help) { setHelpId(unlock.help); setPanel("help"); }
    return result;
  };

  const setSpeed = (speed: number) => {
    game.setSpeed(speed);
    persist({ settings: { ...saveRef.current.settings, speed } });
  };

  const files = save.files;
  return (
    <div class="app">
      <header class="topbar">
        <div class="brand">🏭 <span>ByteWorks</span></div>
        <InventoryBar world={world} />
        <span class="spacer" />
        <button class="btn" onClick={() => setPanel("upgrades")}>⬆️ Upgrades{affordable > 0 && <span class="badge">{affordable}</span>}</button>
        <button class="btn" onClick={() => setPanel("help")}>📖 Help</button>
        <button class="btn" onClick={() => setPanel("save")}>💾 Save</button>
      </header>

      <main class="game">
        <section class="building">
          <nav class="elevator" aria-label="Floors">
            <button class="btn lift" onClick={() => goFloor(floorIndex + 1)} disabled={floorIndex >= FLOORS.length - 1} aria-label="Look one floor up">▲</button>
            <ol class="floor-list">
              {[...FLOORS].reverse().map((f) => (
                <li key={f.id}>
                  <button class={`floor-btn ${f.id === floor.id ? "here" : ""} ${f.unlock && !owned.has(f.unlock) ? "locked" : ""} ${world?.floor === f.id ? "drone" : ""}`}
                    style={{ "--floor": f.color }} onClick={() => goFloor(FLOORS.indexOf(f))} title={f.name}
                    aria-current={f.id === floor.id ? "true" : undefined}>{f.label}</button>
                </li>
              ))}
            </ol>
            <button class="btn lift" onClick={() => goFloor(floorIndex - 1)} disabled={floorIndex <= 0} aria-label="Look one floor down">▼</button>
          </nav>
          <div class="floor-frame" style={{ "--floor": floor.color }}>
            <div class="floor-head">
              <span>{floor.icon} {floor.name}</span>
              <label class="follow">
                <input type="checkbox" checked={save.settings.follow}
                  onChange={(e) => persist({ settings: { ...saveRef.current.settings, follow: (e.target as HTMLInputElement).checked } })} />
                Follow drone
              </label>
            </div>
            {world
              ? <FloorView floor={floor} world={world} animMs={animMs} locked={!!floor.unlock && !owned.has(floor.unlock)} lockedBy={lockedBy} />
              : <div class="floor-locked">Starting the factory…</div>}
          </div>
        </section>

        <CodePanel files={files} active={save.active} windows={windows} editKey={editKey}
          running={running} ready={status === "ready"} speed={save.settings.speed} turbo={owned.has("turbo")} lines={lines}
          onEdit={(text) => persist({ files: { ...saveRef.current.files, [saveRef.current.active]: text } })}
          onSelect={(name) => { persist({ active: name }); setEditKey((k) => k + 1); }}
          onAdd={(name) => { persist({ files: { ...saveRef.current.files, [name]: `# ${name}\n` }, active: name }); setEditKey((k) => k + 1); }}
          onDelete={(name) => {
            const { [name]: _gone, ...rest } = saveRef.current.files;
            persist({ files: rest, active: saveRef.current.active === name ? "main.py" : saveRef.current.active });
            setEditKey((k) => k + 1);
          }}
          onRun={onRun} onStop={() => game.stop()} onSpeed={setSpeed} onClear={() => setLines([])} />
      </main>

      {status === "failed" && <div class="toast err">Python couldn't load. Check your internet connection and refresh.</div>}

      {/* Task 12 adds: panel === "upgrades" → <UpgradePanel/>, panel === "help" → <HelpPanel/> */}
      {panel === "save" && (
        <SaveDialog save={save} running={running} onClose={() => setPanel("none")}
          onLoad={(loaded) => { persist(loaded); game.reload(loaded.world); setEditKey((k) => k + 1); setLines([]); }}
          onResetAll={() => { const fresh = emptySave(); persist(fresh); game.reload(null); setEditKey((k) => k + 1); setLines([]); setPanel("help"); setHelpId("start"); }} />
      )}
      <footer class="foot">Inspired by <em>The Farmer Was Replaced</em>. Python runs in your browser with Pyodide. ▲ ▼ or arrow keys change floors.</footer>
    </div>
  );
}
