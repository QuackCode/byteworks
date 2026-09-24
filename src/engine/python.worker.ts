/// <reference lib="webworker" />
// Runs the whole game (world + player's program) off the main thread. Each drone action blocks here
// for real time, so the page stays smooth while the player watches.

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let py: any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let glue: any;
let ctrl: Int32Array | null = null; // [0] = UI speed x100 (0 = turbo), [1] = wake-up flag set by Stop
let fallbackSpeed = 1;              // used when SharedArrayBuffer isn't available

function uiSpeed(): number {
  return ctrl ? Atomics.load(ctrl, 0) / 100 : fallbackSpeed;
}

function pace(ms: number) {
  const speed = uiSpeed();
  if (speed <= 0) return;                 // turbo
  const wait = ms / speed;
  if (ctrl) {
    Atomics.wait(ctrl, 1, 0, wait);       // returns early if Stop sets ctrl[1]
  } else {
    const end = performance.now() + wait; // no SharedArrayBuffer: busy-wait (Stop restarts the worker)
    while (performance.now() < end) { /* waiting */ }
  }
}

const bridge = {
  pace,
  state: (json: string, animMs: number) => {
    const speed = uiSpeed();
    self.postMessage({ type: "state", state: json, animMs: speed > 0 ? animMs / speed : 0 });
  },
  out: (text: string) => self.postMessage({ type: "print", text }),
};

async function init(data: { files: Record<string, string>; state: string | null; interrupt?: SharedArrayBuffer; ctrl?: SharedArrayBuffer }) {
  const { loadPyodide } = await import(/* @vite-ignore */ PYODIDE_URL);
  py = await loadPyodide();
  if (data.interrupt) py.setInterruptBuffer(new Uint8Array(data.interrupt));
  ctrl = data.ctrl ? new Int32Array(data.ctrl) : null;
  py.registerJsModule("bw_bridge", bridge);
  py.FS.mkdirTree("/home/pyodide/game");
  for (const [name, src] of Object.entries(data.files)) py.FS.writeFile(`/home/pyodide/game/${name}`, src);
  py.runPython("import sys, importlib; sys.path.insert(0, '/home/pyodide'); importlib.invalidate_caches()");
  glue = py.pyimport("game.worker_glue");
  return glue.init(data.state);
}

self.onmessage = async (e: MessageEvent) => {
  const { id, type } = e.data;
  try {
    let result: unknown = null;
    if (type === "init") result = await init(e.data);
    else if (type === "run") {
      fallbackSpeed = e.data.speed;
      result = glue.run(e.data.files, e.data.entry);
    } else if (type === "buy") result = glue.buy(e.data.unlock);
    else if (type === "tree") result = glue.tree();
    else if (type === "buySkin") result = glue.buy_skin(e.data.skin);
    else if (type === "skins") result = glue.skin_list();
    else if (type === "snippet") result = glue.snippet(e.data.code);
    else if (type === "new") result = glue.new_game();
    self.postMessage({ id, ok: true, result });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String(err) });
  }
};
