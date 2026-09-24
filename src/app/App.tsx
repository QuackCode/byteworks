import { useEffect, useRef, useState } from "preact/hooks";
import { game } from "../engine/game";
import type { RunnerStatus, UnlockInfo, WorldState } from "../engine/types";
import { emptySave, loadSave, storeSave, type Save } from "../engine/save";
import { FLOORS } from "../floors";
import { FloorView } from "./FloorView";
import { InventoryBar } from "./InventoryBar";
import { CodePanel, type ConsoleLine } from "./CodePanel";
import { SaveDialog } from "./SaveDialog";
import { ArtDefs, PartIcon } from "./art";
import { UpgradePanel } from "./UpgradePanel";
import { HelpPanel } from "./HelpPanel";

const AUTOSAVE_MS = 5000;
const MAX_WINDOWS = 8;
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
  const [stopping, setStopping] = useState(false);
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
  const addLines = (texts: string[], kind: ConsoleLine["kind"]) =>
    setLines((cur) => [...cur, ...texts.map((text) => ({ text, kind }))].slice(-MAX_LINES));
  const addLine = (text: string, kind: ConsoleLine["kind"]) => addLines([text], kind);

  useEffect(() => {
    game.onStatus = setStatus;
    game.onState = (state, ms) => { setWorld(state); setAnimMs(ms); };
    game.onPrint = (text) => addLines(text.split("\n"), "out");   // prints arrive in batches
    game.onWarning = (message) => {
      addLine(message, "err");
      if (game.latest) persist({ world: game.latest });   // replace the unreadable save right away
    };
    game.setSpeed(1);   // no fast-forward: real-time speed comes only from Drone Speed upgrades
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
  const windows = MAX_WINDOWS;   // code windows are free from the start; Modules unlocks `import` between them
  const affordable = world ? tree.filter((u) => !owned.has(u.id) && u.requires.every((r) => owned.has(r))
    && (!u.quest || (world.quests ?? []).includes(u.quest.id))
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
      setStopping(false);
    }
  };

  const onBuy = async (id: string) => {
    const result = await game.buy(id);
    persist({ world: result.state });
    const unlock = tree.find((u) => u.id === id);
    if (result.ok && unlock?.help) { setHelpId(unlock.help); setPanel("help"); }
    return result;
  };

  const files = save.files;
  return (
    <div class="app">
      <ArtDefs />
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
              <span class="floor-title"><PartIcon part={floor.id === "ASSEMBLY" ? "COMPUTER" : floor.id} size={26} /> {floor.name}</span>
              <label class="follow">
                <input type="checkbox" checked={save.settings.follow}
                  onChange={(e) => persist({ settings: { ...saveRef.current.settings, follow: (e.target as HTMLInputElement).checked } })} />
                Follow drone
              </label>
            </div>
            {world && world.floor !== floor.id && !(floor.unlock && !owned.has(floor.unlock)) && (
              <p class="drone-elsewhere">
                🤖 Your drone is on the {FLOORS.find((f) => f.id === world.floor)?.name ?? world.floor}.
                Bring it here with <code>goto_floor(Floor.{floor.id})</code> in your code.
              </p>
            )}
            {world && floor.unlock && owned.has(floor.unlock) && floor.id !== "ASSEMBLY"
              && world.floors[floor.id]?.grid.every((col) => col.every((tile) => tile[0] === null)) && (
              <p class="drone-elsewhere">
                🧱 This floor starts empty. Build parts here with <code>place(Part.{floor.id})</code>, let them finish,
                then <code>harvest()</code>.{" "}
                <button class="linkish" onClick={() => { setHelpId(floor.unlock!); setPanel("help"); }}>How does this floor work?</button>
              </p>
            )}
            {world
              ? <FloorView floor={floor} world={world} animMs={animMs} locked={!!floor.unlock && !owned.has(floor.unlock)} lockedBy={lockedBy} />
              : <div class="floor-locked">Starting the factory…</div>}
          </div>
        </section>

        <CodePanel files={files} active={save.active} windows={windows} editKey={editKey}
          running={running} stopping={stopping} ready={status === "ready"} lines={lines}
          onEdit={(text) => persist({ files: { ...saveRef.current.files, [saveRef.current.active]: text } })}
          onSelect={(name) => { persist({ active: name }); setEditKey((k) => k + 1); }}
          onAdd={(name) => { persist({ files: { ...saveRef.current.files, [name]: `# ${name}\n` }, active: name }); setEditKey((k) => k + 1); }}
          onRename={(from, to) => {
            const renamed: Record<string, string> = {};
            for (const [name, code] of Object.entries(saveRef.current.files)) renamed[name === from ? to : name] = code;
            persist({ files: renamed, active: saveRef.current.active === from ? to : saveRef.current.active });
            setEditKey((k) => k + 1);
          }}
          onDelete={(name) => {
            const { [name]: _gone, ...rest } = saveRef.current.files;
            persist({ files: rest, active: saveRef.current.active === name ? "main.py" : saveRef.current.active });
            setEditKey((k) => k + 1);
          }}
          onRun={onRun} onStop={() => { setStopping(true); game.stop(); }} onClear={() => setLines([])} />
      </main>

      {status === "failed" && <div class="toast err">Python couldn't load. Check your internet connection and refresh.</div>}

      {panel === "upgrades" && world && (
        <UpgradePanel tree={tree} world={world} running={running} onBuy={onBuy} onClose={() => setPanel("none")}
          onHelp={(id) => { setHelpId(id); setPanel("help"); }} />
      )}
      {panel === "help" && (
        <HelpPanel helpId={helpId} tree={tree} owned={owned} questsDone={new Set(world?.quests ?? [])} running={running}
          onPick={setHelpId} onClose={() => setPanel("none")} />
      )}
      {panel === "save" && (
        <SaveDialog save={save} running={running} onClose={() => setPanel("none")}
          onLoad={(loaded) => { persist(loaded); game.reload(loaded.world); setEditKey((k) => k + 1); setLines([]); }}
          onResetAll={() => { const fresh = emptySave(); persist(fresh); game.reload(null); setEditKey((k) => k + 1); setLines([]); setPanel("help"); setHelpId("start"); }} />
      )}
      <footer class="foot">Inspired by <em>The Farmer Was Replaced</em>. Python runs in your browser with Pyodide. ▲ ▼ or arrow keys change floors.</footer>
    </div>
  );
}
