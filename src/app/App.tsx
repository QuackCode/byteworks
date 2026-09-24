import { useEffect, useMemo, useRef, useState } from "preact/hooks";
import { FLOORS } from "../floors";
import { LEVELS } from "../levels";
import { runner, type RunnerStatus } from "../engine/runner";
import type { CheckResult } from "../engine/events";
import { loadSave, storeSave, type Save } from "../engine/save";
import { daysOnFloor, isDayUnlocked, isFloorUnlocked, nextDay } from "../engine/progress";
import { FloorView } from "./FloorView";
import { Lesson } from "./Lesson";
import { Workbench } from "./Workbench";
import { SaveDialog } from "./SaveDialog";

// Only floors that have levels so far are part of the building.
const BUILT_FLOORS = FLOORS.filter((f) => daysOnFloor(LEVELS, f.id).length > 0);

function isTyping(el: EventTarget | null) {
  const node = el as HTMLElement | null;
  return !!node?.closest?.(".cm-editor, input, textarea, [contenteditable]");
}

export function App() {
  const [save, setSave] = useState<Save>(loadSave);
  const [day, setDay] = useState(() => nextDay(LEVELS, save.completed)?.day ?? 1);
  const level = LEVELS.find((l) => l.day === day) ?? LEVELS[0];
  const [floorId, setFloorId] = useState(level.floor);
  const [slide, setSlide] = useState<"up" | "down" | "">("");
  const [status, setStatus] = useState<RunnerStatus>(runner.status);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<CheckResult | null>(null);
  const [runId, setRunId] = useState(0);
  const [codeVersion, setCodeVersion] = useState(0);
  const [showSave, setShowSave] = useState(false);
  const saveTimer = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => runner.onStatus(setStatus), []);

  const floor = BUILT_FLOORS.find((f) => f.id === floorId) ?? BUILT_FLOORS[0];
  const floorIndex = BUILT_FLOORS.indexOf(floor);
  const floorDays = useMemo(() => daysOnFloor(LEVELS, floor.id), [floor.id]);
  const floorLocked = !isFloorUnlocked(LEVELS, floor.id, save.completed);
  const unlockedDays = LEVELS.filter((l) => isDayUnlocked(l.day, save.completed)).map((l) => l.day);
  const code = save.code[day] ?? level.starter;

  const update = (next: Save) => {
    setSave(next);
    storeSave(next);
  };

  const goFloor = (index: number) => {
    const target = BUILT_FLOORS[index];
    if (!target || target.id === floor.id) return;
    setSlide(index > floorIndex ? "up" : "down");
    setFloorId(target.id);
    // Jump to the next unfinished day on that floor (or its last day)
    const days = daysOnFloor(LEVELS, target.id);
    const pick = days.find((d) => !save.completed.includes(d.day) && isDayUnlocked(d.day, save.completed)) ?? days.at(-1)!;
    if (isDayUnlocked(pick.day, save.completed)) selectDay(pick.day);
  };

  const selectDay = (d: number) => {
    setDay(d);
    setResult(null);
    setCodeVersion((v) => v + 1);
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (isTyping(e.target) || showSave) return;
      if (e.key === "ArrowUp") { e.preventDefault(); goFloor(floorIndex + 1); }
      if (e.key === "ArrowDown") { e.preventDefault(); goFloor(floorIndex - 1); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  // Track the editor's latest text synchronously so Run never uses a stale save
  const latestCode = useRef(code);
  useEffect(() => { latestCode.current = code; }, [day, codeVersion]);
  const trackCode = (text: string) => {
    latestCode.current = text;
    onCodeChange(text);
  };

  const onCodeChange = (text: string) => {
    clearTimeout(saveTimer.current);
    const d = day;
    saveTimer.current = setTimeout(() => {
      setSave((cur) => {
        const next = { ...cur, code: { ...cur.code, [d]: text } };
        storeSave(next);
        return next;
      });
    }, 400);
  };

  const onRun = async () => {
    if (running || status !== "ready") return;
    clearTimeout(saveTimer.current);
    setRunning(true);
    try {
      const src = latestCode.current;
      const r = await runner.check(src, level.check);
      setResult(r);
      setFloorId(level.floor);
      setRunId((n) => n + 1);
      const completed = r.passed && !save.completed.includes(day) ? [...save.completed, day] : save.completed;
      update({ ...save, completed, code: { ...save.code, [day]: src } });
    } catch (e) {
      setResult({ passed: false, message: `Something went wrong running your code: ${e}`, stdout: "", error: null, events: [] });
    } finally {
      setRunning(false);
    }
  };

  const onReset = () => {
    const { [day]: _, ...rest } = save.code;
    update({ ...save, code: rest });
    latestCode.current = level.starter;
    setResult(null);
    setCodeVersion((v) => v + 1);
  };

  const next = LEVELS.find((l) => l.day === day + 1);
  const onNext = () => {
    if (!next) return;
    if (next.floor !== floor.id) {
      const idx = BUILT_FLOORS.findIndex((f) => f.id === next.floor);
      setSlide(idx > floorIndex ? "up" : "down");
      setFloorId(next.floor);
    }
    selectDay(next.day);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const done = save.completed.length;
  const firstDayOnFloor = floorDays[0]?.day ?? 1;

  return (
    <div class="app">
      <header class="topbar">
        <div class="brand">🏭 <span>ByteWorks</span></div>
        <div class="progress" title={`${done} of 30 shifts complete`}>
          <div class="progress-track"><div class="progress-fill" style={{ width: `${(done / 30) * 100}%` }} /></div>
          <span>{done}/30 shifts</span>
        </div>
        <button class="btn small" onClick={() => setShowSave(true)}>💾 Save</button>
      </header>

      <section class="building">
        <nav class="elevator" aria-label="Floors">
          <button class="btn lift" onClick={() => goFloor(floorIndex + 1)} disabled={floorIndex >= BUILT_FLOORS.length - 1}
            aria-label="Go up a floor">▲</button>
          <ol class="floor-list">
            {[...BUILT_FLOORS].reverse().map((f) => {
              const open = isFloorUnlocked(LEVELS, f.id, save.completed);
              return (
                <li key={f.id}>
                  <button class={`floor-btn ${f.id === floor.id ? "here" : ""} ${open ? "" : "locked"}`}
                    style={{ "--floor": f.color }} onClick={() => goFloor(BUILT_FLOORS.indexOf(f))}
                    aria-current={f.id === floor.id ? "true" : undefined} title={f.name}>
                    {f.label}
                  </button>
                </li>
              );
            })}
          </ol>
          <button class="btn lift" onClick={() => goFloor(floorIndex - 1)} disabled={floorIndex <= 0}
            aria-label="Go down a floor">▼</button>
        </nav>
        <div class={`floor-frame slide-${slide}`} key={floor.id} onAnimationEnd={() => setSlide("")}>
          <FloorView floor={floor} days={floorDays} completed={save.completed} unlockedDays={unlockedDays}
            currentDay={day} locked={floorLocked} lockedHint={`Finish Day ${firstDayOnFloor - 1} to open this floor`}
            events={result && level.floor === floor.id ? result.events : []} runId={level.floor === floor.id ? runId : 0}
            onSelectDay={selectDay} />
        </div>
      </section>

      {floorLocked ? (
        <section class="panel locked-panel">
          <h2>🔒 {floor.name} is locked</h2>
          <p>Finish Day {firstDayOnFloor - 1} to take the lift up to this floor.</p>
        </section>
      ) : (
        <>
          <nav class="day-tabs" aria-label="Shifts on this floor">
            {floorDays.map((d) => {
              const open = unlockedDays.includes(d.day);
              const complete = save.completed.includes(d.day);
              return (
                <button key={d.day} class={`day-tab ${d.day === day ? "active" : ""}`} disabled={!open}
                  onClick={() => selectDay(d.day)}>
                  <span class="day-num">{complete ? "✓" : open ? d.day : "🔒"}</span>
                  <span>Day {d.day}: {d.title}</span>
                </button>
              );
            })}
          </nav>
          {level.floor === floor.id && (
            <main class="shift">
              <Lesson level={level} />
              <Workbench level={level} code={code} codeKey={`${day}:${codeVersion}`} status={status}
                running={running} result={result} completed={save.completed.includes(day)} hasNext={!!next}
                onCodeChange={trackCode} onRun={onRun} onReset={onReset} onNext={onNext} />
            </main>
          )}
        </>
      )}

      <footer class="foot">
        Based on <a href="https://github.com/Asabeneh/30-Days-Of-Python" target="_blank" rel="noopener">30 Days of Python</a> by Asabeneh.
        Python runs in your browser with <a href="https://pyodide.org" target="_blank" rel="noopener">Pyodide</a>. Use ▲ ▼ (or the arrow keys) to change floors.
      </footer>

      {showSave && (
        <SaveDialog save={save} onClose={() => setShowSave(false)}
          onLoad={(s) => { update(s); const d = nextDay(LEVELS, s.completed) ?? LEVELS[0]; setFloorId(d.floor); selectDay(d.day); }}
          onResetAll={() => { update({ v: 1, completed: [], code: {} }); setFloorId(0); selectDay(1); }} />
      )}
    </div>
  );
}
