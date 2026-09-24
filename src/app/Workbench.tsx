import { useEffect, useRef, useState } from "preact/hooks";
import type { Level } from "../levels";
import type { CheckResult } from "../engine/events";
import type { RunnerStatus } from "../engine/runner";
import { Editor } from "./Editor";

interface Props {
  level: Level;
  code: string;
  codeKey: string;
  status: RunnerStatus;
  running: boolean;
  result: CheckResult | null;
  completed: boolean;
  hasNext: boolean;
  onCodeChange: (code: string) => void;
  onRun: () => void;
  onReset: () => void;
  onNext: () => void;
}

export function Workbench(p: Props) {
  const [hintsShown, setHintsShown] = useState(0);
  const [confirmReset, setConfirmReset] = useState(false);
  const resultRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    resultRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [p.result]);
  useEffect(() => {
    setHintsShown(0);
    setConfirmReset(false);
  }, [p.level.day]);

  const runLabel = p.running ? "Running…" : p.status === "loading" ? "Starting Python…" : "▶ Run shift";

  return (
    <section class="workbench panel">
      <div class="workbench-head">
        <div>
          <div class="eyebrow">Day {p.level.day} · {p.level.topic}</div>
          <h2>{p.level.title} {p.completed && <span class="done-badge">✓ complete</span>}</h2>
        </div>
      </div>

      <Editor value={p.code} docKey={p.codeKey} onChange={p.onCodeChange} onRun={p.onRun} />

      <div class="actions">
        <button class="btn primary" onClick={p.onRun} disabled={p.running || p.status !== "ready"}>
          {runLabel}
        </button>
        <span class="kbd-hint">or Ctrl + Enter</span>
        <span class="spacer" />
        {confirmReset ? (
          <>
            <span class="kbd-hint">Lose your changes?</span>
            <button class="btn danger small" onClick={() => { p.onReset(); setConfirmReset(false); }}>Yes, reset</button>
            <button class="btn small" onClick={() => setConfirmReset(false)}>Cancel</button>
          </>
        ) : (
          <button class="btn small ghost" onClick={() => setConfirmReset(true)}>↺ Reset code</button>
        )}
      </div>

      {p.status === "failed" && (
        <div class="result fail">
          Python couldn't load. Check your internet connection and refresh the page.
        </div>
      )}

      {p.result && (
        <div class={`result ${p.result.passed ? "pass" : "fail"}`} role="status" ref={resultRef}>
          <div class="result-title">{p.result.passed ? "✅ Shift complete!" : "🔧 Not quite yet"}</div>
          <p class="result-msg">{p.result.message}</p>
          {p.result.passed && p.hasNext && (
            <button class="btn primary" onClick={p.onNext}>Next shift →</button>
          )}
          {p.result.passed && !p.hasNext && <p>🎉 That's every shift available so far. Amazing work!</p>}
        </div>
      )}

      {p.result && (p.result.stdout || p.result.error) && (
        <div class="console">
          <div class="console-title">Output</div>
          <pre>{p.result.stdout}{p.result.error && <span class="err">{p.result.stdout ? "\n" : ""}{p.result.error}</span>}</pre>
        </div>
      )}

      <div class="hints">
        {p.level.hints.slice(0, hintsShown).map((h, i) => (
          <div class="hint" key={i}><strong>Hint {i + 1}:</strong> {h}</div>
        ))}
        {hintsShown < p.level.hints.length && (
          <button class="btn small ghost" onClick={() => setHintsShown(hintsShown + 1)}>
            💡 {hintsShown === 0 ? "Stuck? Show a hint" : `Show hint ${hintsShown + 1} of ${p.level.hints.length}`}
          </button>
        )}
      </div>
    </section>
  );
}
