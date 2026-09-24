import { useEffect, useRef, useState } from "preact/hooks";
import { Editor } from "./Editor";

export interface ConsoleLine { text: string; kind: "out" | "err" | "info" }

interface Props {
  files: Record<string, string>; active: string; windows: number; editKey: number;
  running: boolean; ready: boolean; speed: number; turbo: boolean; lines: ConsoleLine[];
  onEdit: (text: string) => void; onSelect: (name: string) => void;
  onAdd: (name: string) => void; onDelete: (name: string) => void;
  onRun: () => void; onStop: () => void; onSpeed: (speed: number) => void; onClear: () => void;
}

const SPEEDS = [1, 4, 16];
const NAME_OK = /^[a-z_][a-z0-9_]{0,19}$/;

export function CodePanel(p: Props) {
  const names = Object.keys(p.files);
  const [adding, setAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = consoleRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [p.lines]);

  const nameProblem = !newName ? "" : !NAME_OK.test(newName) ? "Use lowercase letters, numbers and _ (no spaces)."
    : p.files[`${newName}.py`] !== undefined ? "That name is taken." : "";

  const add = () => {
    if (!newName || nameProblem) return;
    p.onAdd(`${newName}.py`);
    setAdding(false);
    setNewName("");
  };

  return (
    <section class="code-panel panel">
      <div class="tabs" role="tablist">
        {names.map((name) => (
          <div key={name} class={`tab ${name === p.active ? "active" : ""}`} role="tab" aria-selected={name === p.active}>
            <button class="tab-name" onClick={() => p.onSelect(name)}>{name}</button>
            {name !== "main.py" && !p.running && (confirmDelete === name
              ? <button class="tab-x danger" onClick={() => { p.onDelete(name); setConfirmDelete(null); }} title="Click again to delete">delete?</button>
              : <button class="tab-x" onClick={() => setConfirmDelete(name)} aria-label={`Delete ${name}`}>✕</button>)}
          </div>
        ))}
        {names.length < p.windows && !adding && <button class="tab add" onClick={() => setAdding(true)}>+ New window</button>}
        {adding && (
          <form class="tab add-form" onSubmit={(e) => { e.preventDefault(); add(); }}>
            <input autoFocus value={newName} placeholder="helpers" onInput={(e) => setNewName((e.target as HTMLInputElement).value)} />
            <span>.py</span>
            <button class="btn small" disabled={!newName || !!nameProblem}>Add</button>
            <button type="button" class="btn small ghost" onClick={() => { setAdding(false); setNewName(""); }}>Cancel</button>
          </form>
        )}
      </div>
      {nameProblem && <div class="hint-line">{nameProblem}</div>}

      <Editor value={p.files[p.active]} docKey={`${p.active}:${p.editKey}`} onChange={p.onEdit} onRun={p.onRun} />

      <div class="controls">
        {p.running
          ? <button class="btn danger" onClick={p.onStop}>■ Stop</button>
          : <button class="btn primary" onClick={p.onRun} disabled={!p.ready}>{p.ready ? `▶ Run ${p.active}` : "Starting Python…"}</button>}
        <span class="kbd-hint">Ctrl + Enter</span>
        <span class="spacer" />
        <div class="speed" role="group" aria-label="Speed">
          {SPEEDS.map((s) => (
            <button key={s} class={`btn small ${p.speed === s ? "on" : ""}`} onClick={() => p.onSpeed(s)}>x{s}</button>
          ))}
          {p.turbo && <button class={`btn small ${p.speed === 0 ? "on" : ""}`} onClick={() => p.onSpeed(0)} title="No animation">⚡ Turbo</button>}
        </div>
      </div>

      <div class="console">
        <div class="console-head"><span>Console</span><button class="btn small ghost" onClick={p.onClear}>Clear</button></div>
        <div class="console-body" ref={consoleRef} aria-live="polite">
          {p.lines.length === 0 && <div class="line info">Output from print() and any errors appear here.</div>}
          {p.lines.map((l, i) => <div key={i} class={`line ${l.kind}`}>{l.text}</div>)}
        </div>
      </div>
    </section>
  );
}
