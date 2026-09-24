/// <reference lib="webworker" />
// Runs Python (Pyodide) off the main thread, so a player's infinite loop can't freeze the page.
// The main thread kills and restarts this worker if a run takes too long.

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let py: any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let checker: any;

async function init(files: Record<string, string>) {
  const { loadPyodide } = await import(/* @vite-ignore */ PYODIDE_URL);
  py = await loadPyodide();
  py.FS.mkdirTree("/home/pyodide/factory");
  for (const [name, src] of Object.entries(files)) {
    py.FS.writeFile(`/home/pyodide/factory/${name}`, src);
  }
  py.runPython("import sys, importlib; sys.path.insert(0, '/home/pyodide'); importlib.invalidate_caches()");
  checker = py.pyimport("factory.checker");
}

// These are simulated by the factory (no internet server or database in a browser),
// so never download the real packages for them.
const SIMULATED = /^\s*(import|from)\s+(requests|flask|pymongo)\b.*$/gm;

async function prepare(source: string) {
  // Downloads numpy/pandas etc. the first time a level imports them.
  try {
    await py.loadPackagesFromImports(source.replace(SIMULATED, ""));
  } catch {
    /* a syntax error in the player's code: the checker will explain it */
  }
}

self.onmessage = async (e: MessageEvent) => {
  const { id, type } = e.data;
  try {
    let result: unknown = null;
    if (type === "init") await init(e.data.files);
    else if (type === "prepare") await prepare(e.data.source);
    else if (type === "check") result = JSON.parse(checker.run_check(e.data.code, e.data.check));
    else if (type === "snippet") result = JSON.parse(checker.run_snippet(e.data.code));
    self.postMessage({ id, ok: true, result });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String(err) });
  }
};
