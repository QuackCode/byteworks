import PythonWorker from "./python.worker?worker";
import type { CheckResult, SnippetResult } from "./events";

const factoryFiles = import.meta.glob("../python/factory/*.py", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

const RUN_TIMEOUT_MS = 6000;

export type RunnerStatus = "loading" | "ready" | "failed";

class TimeoutError extends Error {}

interface Pending {
  resolve: (value: unknown) => void;
  reject: (err: Error) => void;
  timer?: ReturnType<typeof setTimeout>;
}

const OVERHEATED =
  "🔥 The machine overheated! Your code was still running after 6 seconds.\n" +
  "This usually means a loop that never stops. Check that your while loop's condition can become False, " +
  "or that something inside the loop moves it towards finishing.";

export class PythonRunner {
  private worker!: Worker;
  private ready!: Promise<unknown>;
  private nextId = 1;
  private pending = new Map<number, Pending>();
  private listeners = new Set<(s: RunnerStatus) => void>();
  status: RunnerStatus = "loading";

  constructor() {
    this.start();
  }

  onStatus(fn: (s: RunnerStatus) => void): () => void {
    this.listeners.add(fn);
    fn(this.status);
    return () => this.listeners.delete(fn);
  }

  private setStatus(s: RunnerStatus) {
    this.status = s;
    this.listeners.forEach((fn) => fn(s));
  }

  private start() {
    this.setStatus("loading");
    this.worker = new PythonWorker();
    this.worker.onmessage = (e: MessageEvent) => {
      const p = this.pending.get(e.data.id);
      if (!p) return;
      clearTimeout(p.timer);
      this.pending.delete(e.data.id);
      if (e.data.ok) p.resolve(e.data.result);
      else p.reject(new Error(e.data.error));
    };
    const files: Record<string, string> = {};
    for (const [path, src] of Object.entries(factoryFiles)) files[path.split("/").pop()!] = src;
    this.ready = this.send({ type: "init", files });
    this.ready.then(
      () => this.setStatus("ready"),
      () => this.setStatus("failed"),
    );
  }

  /** Kill a stuck worker (infinite loop) and boot a fresh one. */
  private restart() {
    this.worker.terminate();
    for (const p of this.pending.values()) {
      clearTimeout(p.timer);
      p.reject(new TimeoutError());
    }
    this.pending.clear();
    this.start();
  }

  private send(msg: object, timeoutMs?: number): Promise<unknown> {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const p: Pending = { resolve, reject };
      if (timeoutMs) p.timer = setTimeout(() => this.restart(), timeoutMs);
      this.pending.set(id, p);
      this.worker.postMessage({ id, ...msg });
    });
  }

  async check(code: string, check: string): Promise<CheckResult> {
    await this.ready;
    await this.send({ type: "prepare", source: `${code}\n${check}` });
    try {
      return (await this.send({ type: "check", code, check }, RUN_TIMEOUT_MS)) as CheckResult;
    } catch (err) {
      if (err instanceof TimeoutError) {
        return { passed: false, message: OVERHEATED, stdout: "", error: null, events: [] };
      }
      throw err;
    }
  }

  async snippet(code: string): Promise<SnippetResult> {
    await this.ready;
    await this.send({ type: "prepare", source: code });
    try {
      return (await this.send({ type: "snippet", code }, RUN_TIMEOUT_MS)) as SnippetResult;
    } catch (err) {
      if (err instanceof TimeoutError) return { stdout: "", error: OVERHEATED };
      throw err;
    }
  }
}

export const runner = new PythonRunner();
