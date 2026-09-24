import GameWorker from "./python.worker?worker";
import type { BuyResult, RunResult, RunnerStatus, SnippetResult, UnlockInfo, WorldState } from "./types";

const packageFiles = import.meta.glob("../python/game/*.py", { query: "?raw", import: "default", eager: true }) as Record<string, string>;
const STOP_WATCHDOG_MS = 1500; // if an interrupt doesn't land in time, restart the worker instead

class Restarted extends Error {}

interface Pending { resolve: (v: unknown) => void; reject: (e: Error) => void }

export class GameRunner {
  readonly isolated = typeof crossOriginIsolated !== "undefined" && crossOriginIsolated;
  private interrupt = this.isolated ? new Uint8Array(new SharedArrayBuffer(1)) : null;
  private ctrl = this.isolated ? new Int32Array(new SharedArrayBuffer(8)) : null;
  private worker!: Worker;
  private ready!: Promise<unknown>;
  private pending = new Map<number, Pending>();
  private nextId = 1;
  private speed = 1;
  private watchdog?: ReturnType<typeof setTimeout>;
  latest: WorldState | null = null;
  running = false;
  onState?: (state: WorldState, animMs: number) => void;
  onPrint?: (text: string) => void;
  onStatus?: (status: RunnerStatus) => void;
  onWarning?: (message: string) => void;
  private stopping = false;

  start(state: WorldState | null) {
    this.onStatus?.("loading");
    this.worker = new GameWorker();
    this.worker.onmessage = (e: MessageEvent) => this.receive(e.data);
    const files: Record<string, string> = {};
    for (const [path, src] of Object.entries(packageFiles)) files[path.split("/").pop()!] = src;
    this.ready = this.call({
      type: "init", files, state: state ? JSON.stringify(state) : null,
      interrupt: this.interrupt?.buffer, ctrl: this.ctrl?.buffer,
    }).then((json) => {
      const booted = JSON.parse(json as string) as { state: WorldState; warning: boolean };
      this.setState(booted.state, 0);
      if (booted.warning) this.onWarning?.("Your saved factory couldn't be read, so a new one was started.");
      this.onStatus?.("ready");
    }, (err) => {
      this.onStatus?.("failed");
      throw err;
    });
  }

  private receive(msg: { id?: number; type?: string; ok?: boolean; result?: unknown; error?: string; state?: string; animMs?: number; text?: string }) {
    if (msg.type === "state") return this.setState(JSON.parse(msg.state!), msg.animMs ?? 0);
    if (msg.type === "print") return this.onPrint?.(msg.text!);
    const p = this.pending.get(msg.id!);
    if (!p) return;
    this.pending.delete(msg.id!);
    if (msg.ok) p.resolve(msg.result);
    else p.reject(new Error(msg.error));
  }

  private setState(state: WorldState, animMs: number) {
    this.latest = state;
    this.onState?.(state, animMs);
  }

  private call(msg: object): Promise<unknown> {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.worker.postMessage({ id, ...msg });
    });
  }

  setSpeed(multiplier: number) {
    this.speed = multiplier;
    if (this.ctrl) Atomics.store(this.ctrl, 0, Math.round(multiplier * 100));
  }

  async run(files: Record<string, string>, entry: string): Promise<RunResult> {
    await this.ready;
    this.running = true;
    if (this.interrupt) this.interrupt[0] = 0;
    if (this.ctrl) { Atomics.store(this.ctrl, 1, 0); Atomics.store(this.ctrl, 0, Math.round(this.speed * 100)); }
    try {
      const result = JSON.parse((await this.call({ type: "run", files: JSON.stringify(files), entry, speed: this.speed })) as string) as RunResult;
      this.setState(result.state, 0);
      return result;
    } catch (err) {
      if (err instanceof Restarted) return { ok: true, stopped: true, state: this.latest! };
      throw err;
    } finally {
      this.running = false;
      this.stopping = false;
      clearTimeout(this.watchdog);
      // A Stop that arrived after the program had already finished must not hit the next command
      if (this.interrupt) this.interrupt[0] = 0;
      if (this.ctrl) Atomics.store(this.ctrl, 1, 0);
    }
  }

  stop() {
    if (!this.running || this.stopping) return;   // a double-click must not start a second watchdog
    this.stopping = true;
    if (this.interrupt && this.ctrl) {
      this.interrupt[0] = 2;                 // SIGINT: Python raises KeyboardInterrupt at the next bytecode
      Atomics.store(this.ctrl, 1, 1);
      Atomics.notify(this.ctrl, 1);          // wake a drone that's mid-action
      this.watchdog = setTimeout(() => this.restart(), STOP_WATCHDOG_MS);
    } else {
      this.restart();
    }
  }

  /** Throw away the current world and start from `state` (a loaded save, or null for a new game). */
  reload(state: WorldState | null) {
    this.latest = state;
    this.restart();
  }

  /** Kill the worker and boot a new one from the latest world state. */
  private restart() {
    this.worker.terminate();
    for (const p of this.pending.values()) p.reject(new Restarted());
    this.pending.clear();
    this.start(this.latest);
  }

  async buy(unlockId: string): Promise<BuyResult> {
    await this.ready;
    const result = JSON.parse((await this.call({ type: "buy", unlock: unlockId })) as string) as BuyResult;
    this.setState(result.state, 0);
    return result;
  }

  async tree(): Promise<UnlockInfo[]> {
    await this.ready;
    return JSON.parse((await this.call({ type: "tree" })) as string);
  }

  async snippet(code: string): Promise<SnippetResult> {
    await this.ready;
    return JSON.parse((await this.call({ type: "snippet", code })) as string);
  }

  async newGame(): Promise<WorldState> {
    await this.ready;
    const state = JSON.parse((await this.call({ type: "new" })) as string) as WorldState;
    this.setState(state, 0);
    return state;
  }
}

export const game = new GameRunner();
