import { useEffect, useRef, useState } from "preact/hooks";
import { Editor } from "./Editor";

export interface ConsoleLine { text: string; kind: "out" | "err" | "info" }

interface Props {
  files: Record<string, string>; active: string; windows: number; editKey: number;
  running: boolean; stopping: boolean; ready: boolean; lines: ConsoleLine[];
  onEdit: (text: string) => void; onSelect: (name: string) => void;
  onAdd: (name: string) => void; onRename: (from: string, to: string) => void; onDelete: (name: string) => void;
  onRun: () => void; onStop: () => void; onClear: () => void;
}

const NAME_OK = /^[a-z_][a-z0-9_]{0,19}$/;
// Window names become module names for `import`, so they can't clash with Python words or allowed modules
const RESERVED = new Set([
  "main", "math", "random", "false", "none", "true", "and", "as", "assert", "async", "await", "break", "class",
  "continue", "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import", "in",
  "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
]);

type Naming = { kind: "add" } | { kind: "rename"; from: string } | null;

export function CodePanel(p: Props) {
  const names = Object.keys(p.files);
  const [naming, setNaming] = useState<Naming>(null);
  const [newName, setNewName] = useState("");
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const consoleRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = consoleRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [p.lines]);

  const unchanged = naming?.kind === "rename" && `${newName}.py` === naming.from;
  const nameProblem = !newName || unchanged ? ""
    : !NAME_OK.test(newName) ? "Use lowercase letters, numbers and _ (no spaces), starting with a letter."
    : RESERVED.has(newName) ? `"${newName}" is a Python word or module name. Pick another name.`
    : p.files[`${newName}.py`] !== undefined ? "That name is taken." : "";

  const startNaming = (mode: Naming) => {
    setNaming(mode);
    setNewName(mode?.kind === "rename" ? mode.from.replace(/\.py$/, "") : "");
  };

  const submit = () => {
    if (!naming || !newName || nameProblem) return;
    if (naming.kind === "add") p.onAdd(`${newName}.py`);
    else if (!unchanged) p.onRename(naming.from, `${newName}.py`);
    startNaming(null);
  };

  const nameForm = (
    <form class="tab add-form" onSubmit={(e) => { e.preventDefault(); submit(); }}>
      <input autoFocus value={newName} placeholder="cpu_floor" aria-label="Window name"
        onInput={(e) => setNewName((e.target as HTMLInputElement).value)} />
      <span>.py</span>
      <button class="btn small" disabled={!newName || !!nameProblem}>{naming?.kind === "rename" ? "Rename" : "Add"}</button>
      <button type="button" class="btn small ghost" onClick={() => startNaming(null)}>Cancel</button>
    </form>
  );

  return (
    <section class="code-panel panel">
      <div class="tabs" role="tablist">
        {names.map((name) => naming?.kind === "rename" && naming.from === name ? <span key={name}>{nameForm}</span> : (
          <div key={name} class={`tab ${name === p.active ? "active" : ""}`} role="tab" aria-selected={name === p.active}>
            <button class="tab-name" onClick={() => p.onSelect(name)}>{name}</button>
            {name !== "main.py" && name === p.active && !p.running && (
              <button class="tab-x" onClick={() => startNaming({ kind: "rename", from: name })} aria-label={`Rename ${name}`} title="Rename">✎</button>
            )}
            {name !== "main.py" && !p.running && (confirmDelete === name
              ? <button class="tab-x danger" onClick={() => { p.onDelete(name); setConfirmDelete(null); }} title="Click again to delete">delete?</button>
              : <button class="tab-x" onClick={() => setConfirmDelete(name)} aria-label={`Delete ${name}`} title="Delete">✕</button>)}
          </div>
        ))}
        {names.length < p.windows && !naming && <button class="tab add" onClick={() => startNaming({ kind: "add" })} title="New code window">+ New window</button>}
        {naming?.kind === "add" && nameForm}
      </div>
      {nameProblem && <div class="hint-line">{nameProblem}</div>}

      <Editor value={p.files[p.active]} docKey={`${p.active}:${p.editKey}`} onChange={p.onEdit} onRun={p.onRun} />

      <div class="controls">
        {p.running
          ? <button class="btn danger" onClick={p.onStop} disabled={p.stopping}>{p.stopping ? "Stopping…" : "■ Stop"}</button>
          : <button class="btn primary" onClick={p.onRun} disabled={!p.ready}>{p.ready ? `▶ Run ${p.active}` : "Starting Python…"}</button>}
        <span class="kbd-hint">Ctrl + Enter</span>
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
