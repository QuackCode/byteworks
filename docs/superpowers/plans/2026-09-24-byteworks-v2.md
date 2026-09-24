# ByteWorks v2 (Automation Game) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild ByteWorks as a *Farmer Was Replaced*-style browser game. Players write Python that drives a drone around factory-floor grids live, harvest computer parts, and spend them on an upgrade tree that unlocks Python features, speed, bigger grids and new floors.

**Architecture:** All game rules live in a pure-Python package (`src/python/game/`) that is unit-tested with CPython. In the browser, a Pyodide Web Worker holds the world **and** runs the player's program. Each drone action advances a game clock, then blocks for a real-time delay (`Atomics.wait` when the page is cross-origin isolated, otherwise a busy-wait) and posts the world state to the main thread. The main thread (Preact) only renders and sends commands. Stop uses Pyodide's interrupt buffer. `coi-serviceworker` makes GitHub Pages cross-origin isolated.

**Tech Stack:** Vite 8, TypeScript, Preact, CodeMirror 6, marked, Pyodide v314.0.7 (jsDelivr CDN), coi-serviceworker, vitest, Python 3.14 `unittest`.

**Spec:** `docs/specs/2026-09-24-byteworks-automation-design.md`

## Global Constraints

- Static site only: free hosting on GitHub Pages, no servers, no accounts, ~30+ simultaneous players.
- Only files inside `~/projects/byteworks` may be read or changed. Never list or open other folders in `~/projects`.
- Covers core Python only (30 Days of Python days 1–17 and 21). No Flask, MongoDB, pandas/NumPy, scraping, APIs, venv/pip, regex or file handling.
- Pyodide URL: `https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs` (Python 3.14, matching local and CI Python).
- Save key: `byteworks.save.v2`. Save-code prefix: `BW2.`. v1 saves are ignored.
- All balance numbers live only in `src/python/game/balance.py`.
- Floors, bottom to top: `RAM, CPU, SSD, BOARD, GPU, ASSEMBLY`. ▲/▼ buttons and arrow keys move the **camera**, and a "follow drone" toggle is on by default.
- Game time only advances while a program runs. Speed upgrades change real-time speed only, never tick costs.
- Every user-facing error names the line and says what to do next, in plain English aimed at complete beginners.
- Wrap all `localStorage` access in try/catch.
- Commit after every task.

## Review Focus

- **Pressing Stop while the drone is mid-`while True:`** must stop within one action, keep all harvested parts, and leave Run working again. Tested in Task 8 (browser) and by `StopRun` in Task 6.
- **Page not cross-origin isolated** (service worker blocked, first load before the SW takes control): the game must still run (busy-wait pacing), and Stop must restart the worker from the latest state without losing progress. Covered in Task 8.
- **A program that loops without any drone action** (`while True: pass`) must not freeze the tab: the Stop button still works. Covered in Task 8.
- **Harvesting a faulty motherboard with no `try/except`** must stop the program with the friendly `FaultyBoardError` message pointing at the player's line, not a stack trace from `game/world.py`. Tested in Task 6.
- **Locked feature inside an imported helper file** must be reported with that file's name and line, and the program must not start. Tested in Task 6.

---

## File Structure

```
src/python/game/
  __init__.py      package marker
  balance.py       every tunable number
  world.py         World, Tile, FaultyBoardError, floors, clock, rules, state (de)serialisation
  unlocks.py       the upgrade tree (Unlock list), buy(), tree_json()
  gating.py        AST checks: which Python features/builtins/API names are unlocked
  errors.py        friendly_error() (ported from v1 checker)
  api.py           Api: player-facing functions + namespace, tick spending, pacing hooks, StopRun
  runner.py        run_program(): gating → builtins with gated import → exec → result
  sandbox.py       run_snippet() for help-page "Try it" boxes
  worker_glue.py   the thin layer the Pyodide worker calls (init/run/buy/tree/snippet/state)
src/engine/
  python.worker.ts Pyodide worker: loads game package, bridge (pace/state/out), message handling
  game.ts          GameRunner (main thread): worker lifecycle, SAB control, run/stop/buy/speed
  types.ts         WorldState, Tile, UnlockInfo, RunResult TS types
  save.ts          v2 save load/store/encode/decode
src/app/
  App.tsx          layout + state wiring
  FloorView.tsx    SVG grid of one floor, drone, lift controls, Assembly order card
  InventoryBar.tsx part counts
  CodePanel.tsx    file tabs, Editor, Run/Stop, speed buttons, console
  Editor.tsx       (kept from v1)
  UpgradePanel.tsx upgrade tree
  HelpPanel.tsx    help pages with Try-it boxes
  SaveDialog.tsx   (kept, updated for v2)
  styles.css       (restyled; system fonts)
src/help/*.md      one help page per unlock + start + floors
src/floors.ts      floor display info (icon, colour, label)
public/coi-serviceworker.min.js
tests/test_game.py       world/unlocks/gating/runner tests (unittest)
tests/test_progress.py   reference bots play the whole game headless
tests/bots/*.py          the reference bot programs
tests/save.test.ts       vitest
```

Removed: `src/levels/`, `src/python/factory/`, `tests/run_levels.py`, `tests/engine.test.ts`, `src/engine/{events,progress,runner}.ts`, `src/app/{Lesson,Workbench}.tsx`. The v1 lessons are first moved to `src/help/_v1/` as source material for help pages (Task 1), then deleted in Task 12.

---

### Task 1: Clear out v1 and set up the Python test harness

**Files:**
- Move: `src/levels/dayNN/lesson.md` → `src/help/_v1/dayNN.md` (all 30)
- Create: `src/python/game/errors.py` (from `src/python/factory/checker.py:friendly_error`)
- Create: `src/python/game/__init__.py`, `tests/test_game.py`
- Delete: `src/levels/`, `src/python/factory/`, `tests/run_levels.py`, `tests/engine.test.ts`, `src/engine/events.ts`, `src/engine/progress.ts`
- Modify: `package.json` scripts

**Interfaces:**
- Produces: `friendly_error(exc: BaseException, user_files: set[str]) -> str` in `game.errors`

- [ ] **Step 1: Move lessons and delete v1 content**

```bash
cd ~/projects/byteworks
mkdir -p src/help/_v1
for d in src/levels/day*; do git mv "$d/lesson.md" "src/help/_v1/$(basename $d).md"; done
git rm -rq src/levels src/python/factory tests/run_levels.py tests/engine.test.ts src/engine/events.ts src/engine/progress.ts
rm -rf src/python/factory
mkdir -p src/python/game tests/bots
touch src/python/game/__init__.py
```

- [ ] **Step 2: Write the failing test for friendly errors**

`tests/test_game.py`:
```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "python"))

from game.errors import friendly_error  # noqa: E402


def raise_in(code, filename="main.py"):
    try:
        exec(compile(code, filename, "exec"), {})
    except BaseException as exc:  # noqa: BLE001
        return exc
    raise AssertionError("code did not raise")


class ErrorTests(unittest.TestCase):
    def test_names_line_and_type(self):
        msg = friendly_error(raise_in("x = 1\nprint(y)\n"), {"main.py"})
        self.assertTrue(msg.startswith("Line 2: NameError"))
        self.assertIn("doesn't know that name", msg)

    def test_syntax_error_line(self):
        try:
            compile("print('hi'\n", "main.py", "exec")
        except SyntaxError as exc:
            msg = friendly_error(exc, {"main.py"})
        self.assertTrue(msg.startswith("Line 1: SyntaxError"))

    def test_reports_line_in_other_user_file(self):
        msg = friendly_error(raise_in("1/0", "helpers.py"), {"main.py", "helpers.py"})
        self.assertIn("helpers.py line 1", msg)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run it to check it fails**

Run: `python3 -m unittest discover -s tests -p "test_*.py"`
Expected: FAIL with `ModuleNotFoundError: No module named 'game.errors'`

- [ ] **Step 4: Implement `errors.py`**

`src/python/game/errors.py`:
```python
"""Turn Python exceptions into beginner-friendly messages that point at the player's own line."""
import traceback

EXPLAIN = {
    "SyntaxError": "Python couldn't read this line. Look for a missing bracket, quote or colon (:).",
    "IndentationError": "The spacing at the start of this line is wrong. Code inside if/while/for/def must be indented by 4 spaces.",
    "NameError": "Python doesn't know that name. Check the spelling, or make sure you created it before using it.",
    "TypeError": "You mixed up types, e.g. adding a number to a string, or calling something the wrong way.",
    "ValueError": "The type was right but the value wasn't.",
    "IndexError": "You asked for a position that doesn't exist in the list. Remember: counting starts at 0.",
    "KeyError": "That key isn't in the dictionary. Check the spelling and capital letters.",
    "AttributeError": "That thing doesn't have the method or attribute you asked for.",
    "ZeroDivisionError": "You divided by zero. Even a factory can't do that!",
    "RecursionError": "A function kept calling itself forever.",
    "ModuleNotFoundError": "There's no code window with that name. Check the spelling (no .py in the import).",
    "FaultyBoardError": "You harvested a faulty motherboard! Check is_faulty() first and replace faulty boards with place(Part.BOARD). Once you unlock Exceptions you can also catch it with try/except.",
}


def _where(exc, user_files):
    """(file, line) of the deepest frame that belongs to the player's code."""
    if isinstance(exc, SyntaxError) and exc.filename in user_files:
        return exc.filename, exc.lineno
    found = (None, None)
    for frame, lineno in traceback.walk_tb(exc.__traceback__):
        if frame.f_code.co_filename in user_files:
            found = (frame.f_code.co_filename, lineno)
    return found


def friendly_error(exc, user_files):
    name = type(exc).__name__
    file, line = _where(exc, user_files)
    if line is None:
        where = ""
    elif file == "main.py" or len(user_files) == 1:
        where = f"Line {line}: "
    else:
        where = f"{file} line {line}: "
    detail = exc.msg if isinstance(exc, SyntaxError) else str(exc)
    return f"{where}{name}: {detail}\n{EXPLAIN.get(name, '')}".strip()
```

Note: `main.py` errors say `Line N:` and other files say `helpers.py line N:`. The "run" entry file is always passed as the first user file (Task 6), and the test above uses `main.py`.

- [ ] **Step 5: Update package.json scripts**

Replace the `scripts` block with:
```json
"scripts": {
  "dev": "vite",
  "build": "tsc --noEmit && vite build",
  "preview": "vite preview",
  "test": "vitest run && npm run test:py",
  "test:py": "python3 -m unittest discover -s tests -p \"test_*.py\""
}
```

- [ ] **Step 6: Run the tests to check they pass**

Run: `npm run test:py`
Expected: `Ran 3 tests ... OK`

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "v2: remove tutorial levels, add friendly error module and Python test harness"
```

---

### Task 2: World core: RAM floor, movement, harvesting, clock, save state

**Files:**
- Create: `src/python/game/balance.py`, `src/python/game/world.py`
- Test: `tests/test_game.py` (add `WorldCoreTests`)

**Interfaces:**
- Produces (used by every later Python task):
  - `balance`: `MS_PER_TICK`, `START_SIZE`, `MAX_SIZE`, `ACTION_TICKS: dict[str,int]`, `GROW_TICKS: dict[str,(int,int)]`, `PLACE_COST: dict[str,dict[str,int]]`, `YIELD: dict[str,int]`, `FAULT_CHANCE`, `SPEEDS: list[float]`, `ORDER_BASE: dict[str,int]`, `WIN_COMPUTERS`
  - `world.FLOORS = ["RAM","CPU","SSD","BOARD","GPU","ASSEMBLY"]`, `world.PARTS = ["RAM","CPU","SSD","BOARD","GPU","COMPUTER"]`, `world.DIRS = {"North":(0,1),"East":(1,0),"South":(0,-1),"West":(-1,0)}`
  - `class Tile(part=None, ready_at=0, faulty=False, score=None, planted_at=0)` with `.to_json() -> list` and `Tile.from_json(list)`
  - `class World(seed=1)` with attributes `seed, rng, clock, inventory, unlocks:set[str], speed_level:int, floors:dict[str,dict], floor:str, x:int, y:int, order:dict|None, orders_done:int`
  - `World` methods: `open_floor(name)`, `resize(name, size)`, `size(name=None) -> int`, `here() -> Tile`, `is_ready(tile) -> bool`, `move(direction) -> bool`, `harvest() -> int`, `to_state() -> dict`, `World.from_state(dict) -> World`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_game.py` (above the `if __name__` block):
```python
from game import balance as B  # noqa: E402
from game.world import World, Tile  # noqa: E402


class WorldCoreTests(unittest.TestCase):
    def test_new_world_has_ready_ram_grid(self):
        w = World(seed=1)
        self.assertEqual(w.floor, "RAM")
        self.assertEqual(w.size(), B.START_SIZE)
        self.assertEqual(w.here().part, "RAM")
        self.assertTrue(w.is_ready(w.here()))

    def test_move_wraps_around(self):
        w = World()
        w.move("West")
        self.assertEqual((w.x, w.y), (B.START_SIZE - 1, 0))
        w.move("South")
        self.assertEqual((w.x, w.y), (B.START_SIZE - 1, B.START_SIZE - 1))

    def test_move_rejects_bad_direction(self):
        with self.assertRaises(ValueError):
            World().move("Up")

    def test_harvest_ram_then_regrow(self):
        w = World()
        self.assertEqual(w.harvest(), 1)
        self.assertEqual(w.inventory["RAM"], 1)
        self.assertEqual(w.harvest(), 0)  # not regrown yet
        w.clock += B.GROW_TICKS["RAM"][1]
        self.assertEqual(w.harvest(), 1)

    def test_state_round_trip_is_exact(self):
        w = World(seed=7)
        w.harvest(); w.move("East"); w.clock += 123
        w.open_floor("CPU")
        copy = World.from_state(w.to_state())
        self.assertEqual(copy.to_state(), w.to_state())
        self.assertEqual(copy.rng.random(), w.rng.random())

    def test_tile_json(self):
        t = Tile("GPU", 50, False, 7, 10)
        self.assertEqual(Tile.from_json(t.to_json()).to_json(), ["GPU", 50, False, 7, 10])
```

- [ ] **Step 2: Run them to check they fail**

Run: `npm run test:py`
Expected: FAIL with `ModuleNotFoundError: No module named 'game.balance'`

- [ ] **Step 3: Write `balance.py`**

```python
"""Every number that decides how ByteWorks feels. Tune here, and nowhere else."""

MS_PER_TICK = 2          # real milliseconds per game tick at speed x1 (a 100-tick move = 0.2 s)
START_SIZE = 3
MAX_SIZE = 8

ACTION_TICKS = {
    "harvest": 100, "move": 100, "place": 100, "swap": 100,
    "print": 50, "goto_floor": 400, "assemble": 200, "sense": 1,
}

# (min, max) ticks for a part to become ready after it is planted / harvested
GROW_TICKS = {"RAM": (250, 350), "CPU": (1200, 2000), "SSD": (1800, 2600), "BOARD": (2500, 3500), "GPU": (800, 1200)}

PLACE_COST = {"CPU": {}, "SSD": {"RAM": 3, "CPU": 1}, "BOARD": {"SSD": 2}, "GPU": {"BOARD": 1, "CPU": 2}}
YIELD = {"RAM": 1, "CPU": 1, "SSD": 2, "BOARD": 1, "GPU": 1}
FAULT_CHANCE = 0.2

# Real-time speed multiplier for each Speed upgrade level (index = level)
SPEEDS = [1, 1.5, 2, 3, 4, 6]

# Final Assembly orders: base quantity per part, scaled up as more orders are completed
ORDER_BASE = {"RAM": 20, "CPU": 10, "SSD": 8, "BOARD": 4, "GPU": 4}
WIN_COMPUTERS = 10
```

- [ ] **Step 4: Write `world.py` (core parts only; Task 3 adds the other floors)**

```python
"""The ByteWorks factory: floors of tiles, one drone, an inventory and a game clock.

Time only moves when the drone acts (the Api adds ticks), so everything is deterministic.
Grids are indexed grid[x][y]; y = 0 is the South edge and North is +y.
"""
import random

from . import balance as B

FLOORS = ["RAM", "CPU", "SSD", "BOARD", "GPU", "ASSEMBLY"]
PARTS = ["RAM", "CPU", "SSD", "BOARD", "GPU", "COMPUTER"]
DIRS = {"North": (0, 1), "East": (1, 0), "South": (0, -1), "West": (-1, 0)}


class FaultyBoardError(Exception):
    """Raised when the drone harvests a faulty motherboard."""


class Tile:
    __slots__ = ("part", "ready_at", "faulty", "score", "planted_at")

    def __init__(self, part=None, ready_at=0, faulty=False, score=None, planted_at=0):
        self.part = part
        self.ready_at = ready_at
        self.faulty = faulty
        self.score = score
        self.planted_at = planted_at

    def to_json(self):
        return [self.part, self.ready_at, self.faulty, self.score, self.planted_at]

    @classmethod
    def from_json(cls, data):
        return cls(*data)


class World:
    def __init__(self, seed=1):
        self.seed = seed
        self.rng = random.Random(seed)
        self.clock = 0
        self.inventory = {p: 0 for p in PARTS}
        self.unlocks = set()
        self.speed_level = 0
        self.floors = {}
        self.floor = "RAM"
        self.x = 0
        self.y = 0
        self.order = None
        self.orders_done = 0
        self.open_floor("RAM")

    # ---------------------------------------------------------------- floors
    def open_floor(self, name):
        if name in self.floors:
            return
        size = 1 if name == "ASSEMBLY" else B.START_SIZE
        self.floors[name] = {"size": size, "grid": [[self._fresh_tile(name) for _ in range(size)] for _ in range(size)]}
        if name == "ASSEMBLY" and self.order is None:
            self.new_order()

    def _fresh_tile(self, floor):
        return Tile("RAM", 0) if floor == "RAM" else Tile()

    def resize(self, name, size):
        old = self.floors[name]
        grid = [[old["grid"][x][y] if x < old["size"] and y < old["size"] else self._fresh_tile(name)
                 for y in range(size)] for x in range(size)]
        self.floors[name] = {"size": size, "grid": grid}
        if self.floor == name:
            self.x %= size
            self.y %= size

    def size(self, name=None):
        return self.floors[name or self.floor]["size"]

    def grid(self, name=None):
        return self.floors[name or self.floor]["grid"]

    def here(self):
        return self.grid()[self.x][self.y]

    def is_ready(self, tile):
        return tile.part is not None and self.clock >= tile.ready_at

    def grow_time(self, part):
        low, high = B.GROW_TICKS[part]
        return self.rng.randint(low, high)

    # ---------------------------------------------------------------- actions
    def move(self, direction):
        if direction not in DIRS:
            raise ValueError("move() needs a direction: North, East, South or West")
        dx, dy = DIRS[direction]
        n = self.size()
        self.x = (self.x + dx) % n
        self.y = (self.y + dy) % n
        return True

    def harvest(self):
        """Collect the part under the drone. Returns how many parts were gained."""
        tile = self.here()
        if tile.part is None:
            return 0
        if tile.part == "RAM":
            if not self.is_ready(tile):
                return 0
            gained = B.YIELD["RAM"]
            tile.planted_at = self.clock
            tile.ready_at = self.clock + self.grow_time("RAM")
            self.inventory["RAM"] += gained
            return gained
        return self._harvest_placed(tile)

    def _harvest_placed(self, tile):
        # Filled in by Task 3 (CPU/SSD/BOARD/GPU rules)
        raise NotImplementedError

    def new_order(self):
        # Filled in by Task 3
        self.order = None

    # ---------------------------------------------------------------- saving
    def to_state(self):
        version, internal, gauss = self.rng.getstate()
        return {
            "seed": self.seed,
            "clock": self.clock,
            "inventory": dict(self.inventory),
            "unlocks": sorted(self.unlocks),
            "speed_level": self.speed_level,
            "floors": {name: {"size": f["size"], "grid": [[t.to_json() for t in col] for col in f["grid"]]}
                       for name, f in self.floors.items()},
            "floor": self.floor,
            "x": self.x,
            "y": self.y,
            "order": dict(self.order) if self.order else None,
            "orders_done": self.orders_done,
            "rng": [version, list(internal), gauss],
        }

    @classmethod
    def from_state(cls, state):
        w = cls.__new__(cls)
        w.seed = state["seed"]
        w.rng = random.Random()
        version, internal, gauss = state["rng"]
        w.rng.setstate((version, tuple(internal), gauss))
        w.clock = state["clock"]
        w.inventory = {p: state["inventory"].get(p, 0) for p in PARTS}
        w.unlocks = set(state["unlocks"])
        w.speed_level = state["speed_level"]
        w.floors = {name: {"size": f["size"], "grid": [[Tile.from_json(t) for t in col] for col in f["grid"]]}
                    for name, f in state["floors"].items()}
        w.floor = state["floor"]
        w.x = state["x"]
        w.y = state["y"]
        w.order = dict(state["order"]) if state["order"] else None
        w.orders_done = state["orders_done"]
        return w
```

- [ ] **Step 5: Run the tests to check they pass**

Run: `npm run test:py`
Expected: all `WorldCoreTests` and `ErrorTests` pass.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "v2: world core (RAM floor, movement, harvest, clock, state)"
```

---

### Task 3: Placeable floors: CPU, SSD, motherboards, GPUs, lift, Final Assembly orders

**Files:**
- Modify: `src/python/game/world.py`
- Test: `tests/test_game.py` (add `FloorRulesTests`)

**Interfaces:**
- Consumes: Task 2's `World`, `Tile`, `balance`.
- Produces: `World.place(part) -> bool`, `World.can_harvest() -> bool`, `World.get_part() -> str|None`, `World.is_faulty() -> bool`, `World.measure() -> int|None`, `World.swap(direction) -> bool`, `World.goto_floor(name) -> bool`, `World.gpu_grid_sorted() -> bool`, `World.new_order() -> None`, `World.assemble() -> bool`, `World.harvest()` raising `FaultyBoardError` for faulty boards.

Rules (from the spec):
- `place(part)`: only on the floor with the same name, only on an **empty** tile or a **faulty ready board** (replacing it), only if the inventory covers `PLACE_COST[part]`. Otherwise it returns `False` and nothing is paid.
- Harvesting a placed part (CPU/SSD/BOARD/GPU) before it is ready **destroys** it (the tile becomes empty) and gains nothing.
- BOARD: faulty is decided on place (`rng.random() < FAULT_CHANCE`). `is_faulty()` is True only when the board is ready. Harvesting a ready faulty board raises `FaultyBoardError` and leaves the tile as it is. Harvesting a good ready board looks for the **largest k×k square (k ≥ 2, no wrap)** containing the drone's tile in which every tile is a good ready board. If found, it gains `k**3` and clears the square; otherwise it gains `YIELD` and clears this tile.
- GPU: `score = rng.randint(0, 9)` on place. `measure()` returns it for any GPU tile (ready or not). `swap(dir)` swaps with the neighbour tile (no wrap; returns False at the edge). Harvesting a ready GPU when `gpu_grid_sorted()` is True gains `n*n` for every chip and clears the whole grid. Otherwise it gains 1 and clears this tile. Sorted = every tile is a ready GPU, each row non-decreasing going East, each column non-decreasing going North.
- `goto_floor(name)`: False if the floor isn't open, else it switches floor and wraps x, y into range.
- ASSEMBLY: `new_order()` picks `min(5, 2 + orders_done // 3)` part kinds, each quantity `ORDER_BASE[p] * rng.randint(1, 2) * (1 + orders_done // 4)`. `assemble()` (drone must be on ASSEMBLY) consumes the order, gives `COMPUTER += 1`, `orders_done += 1`, makes a new order and returns True. Otherwise it returns False.

- [ ] **Step 1: Write the failing tests**

```python
from game.world import FaultyBoardError  # noqa: E402


def world_on(floor, seed=1, **inventory):
    w = World(seed=seed)
    for f in ("CPU", "SSD", "BOARD", "GPU", "ASSEMBLY"):
        w.open_floor(f)
    w.goto_floor(floor)
    w.inventory.update(inventory)
    return w


def fill(w, part, faulty=False, score=None):
    n = w.size()
    for x in range(n):
        for y in range(n):
            w.grid()[x][y] = Tile(part, 0, faulty, score, 0)


class FloorRulesTests(unittest.TestCase):
    def test_place_cpu_bakes_then_harvests(self):
        w = world_on("CPU")
        self.assertTrue(w.place("CPU"))
        self.assertFalse(w.can_harvest())
        w.clock += B.GROW_TICKS["CPU"][1]
        self.assertTrue(w.can_harvest())
        self.assertEqual(w.harvest(), 1)
        self.assertIsNone(w.get_part())

    def test_early_harvest_destroys(self):
        w = world_on("CPU")
        w.place("CPU")
        self.assertEqual(w.harvest(), 0)
        self.assertIsNone(w.get_part())
        self.assertEqual(w.inventory["CPU"], 0)

    def test_place_rules(self):
        w = world_on("SSD")
        self.assertFalse(w.place("CPU"))           # wrong floor
        self.assertFalse(w.place("SSD"))           # can't afford
        w.inventory.update(RAM=3, CPU=1)
        self.assertTrue(w.place("SSD"))
        self.assertEqual((w.inventory["RAM"], w.inventory["CPU"]), (0, 0))
        w.inventory.update(RAM=3, CPU=1)
        self.assertFalse(w.place("SSD"))           # tile occupied
        self.assertEqual(w.inventory["RAM"], 3)    # nothing paid

    def test_faulty_board_raises_and_can_be_replaced(self):
        w = world_on("BOARD", SSD=2)
        w.grid()[0][0] = Tile("BOARD", 0, True, None, 0)
        self.assertTrue(w.is_faulty())
        self.assertTrue(w.can_harvest())
        with self.assertRaises(FaultyBoardError):
            w.harvest()
        self.assertTrue(w.place("BOARD"))
        self.assertEqual(w.inventory["SSD"], 0)

    def test_board_square_merges(self):
        w = world_on("BOARD")
        fill(w, "BOARD")
        self.assertEqual(w.harvest(), 27)          # 3x3 square -> 3**3
        self.assertTrue(all(t.part is None for col in w.grid() for t in col))

    def test_board_with_one_fault_merges_smaller_square(self):
        w = world_on("BOARD")
        fill(w, "BOARD")
        w.grid()[2][2].faulty = True
        self.assertEqual(w.harvest(), 8)           # best square containing (0,0) is 2x2

    def test_gpu_sorted_bonus(self):
        w = world_on("GPU")
        n = w.size()
        for x in range(n):
            for y in range(n):
                w.grid()[x][y] = Tile("GPU", 0, False, x + y, 0)
        self.assertTrue(w.gpu_grid_sorted())
        self.assertEqual(w.harvest(), n * n * n * n)

    def test_gpu_unsorted_and_swap(self):
        w = world_on("GPU")
        fill(w, "GPU", score=5)
        w.grid()[0][0].score = 9
        self.assertFalse(w.gpu_grid_sorted())
        self.assertEqual(w.measure(), 9)
        self.assertFalse(w.swap("West"))           # edge: no wrap
        self.assertTrue(w.swap("East"))
        self.assertEqual(w.measure(), 5)
        self.assertEqual(w.harvest(), 1)

    def test_goto_floor(self):
        w = World()
        self.assertFalse(w.goto_floor("CPU"))      # not open yet
        w.open_floor("CPU")
        self.assertTrue(w.goto_floor("CPU"))
        self.assertEqual(w.floor, "CPU")

    def test_orders_and_assemble(self):
        w = world_on("ASSEMBLY")
        order = dict(w.order)
        self.assertGreaterEqual(len(order), 2)
        self.assertFalse(w.assemble())
        for part, qty in order.items():
            w.inventory[part] = qty
        self.assertTrue(w.assemble())
        self.assertEqual(w.inventory["COMPUTER"], 1)
        self.assertTrue(all(w.inventory[p] == 0 for p in order))
        self.assertNotEqual(w.order, None)

    def test_assemble_needs_assembly_floor(self):
        w = world_on("RAM")
        for part, qty in w.order.items():
            w.inventory[part] = qty
        self.assertFalse(w.assemble())
```

- [ ] **Step 2: Run them to check they fail**

Run: `npm run test:py`
Expected: FAIL with `AttributeError: 'World' object has no attribute 'goto_floor'`

- [ ] **Step 3: Implement the rules in `world.py`**

Replace the `_harvest_placed` and `new_order` stubs and add the methods below inside `class World`:
```python
    # ---------------------------------------------------------------- sensing
    def get_part(self):
        return self.here().part

    def can_harvest(self):
        return self.is_ready(self.here())

    def is_faulty(self):
        tile = self.here()
        return tile.part == "BOARD" and self.is_ready(tile) and tile.faulty

    def measure(self):
        tile = self.here()
        return tile.score if tile.part == "GPU" else None

    # ---------------------------------------------------------------- building
    def place(self, part):
        if part not in B.PLACE_COST or part != self.floor:
            return False
        tile = self.here()
        replacing_fault = tile.part == "BOARD" and self.is_ready(tile) and tile.faulty
        if tile.part is not None and not replacing_fault:
            return False
        cost = B.PLACE_COST[part]
        if any(self.inventory[p] < n for p, n in cost.items()):
            return False
        for p, n in cost.items():
            self.inventory[p] -= n
        faulty = part == "BOARD" and self.rng.random() < B.FAULT_CHANCE
        score = self.rng.randint(0, 9) if part == "GPU" else None
        self.grid()[self.x][self.y] = Tile(part, self.clock + self.grow_time(part), faulty, score, self.clock)
        return True

    def _harvest_placed(self, tile):
        if not self.is_ready(tile):
            self.grid()[self.x][self.y] = Tile()      # harvested too early: destroyed
            return 0
        part = tile.part
        if part == "BOARD":
            if tile.faulty:
                raise FaultyBoardError(f"The motherboard at {(self.x, self.y)} is faulty!")
            gained = self._harvest_board_square()
        elif part == "GPU" and self.gpu_grid_sorted():
            n = self.size()
            gained = n * n * n * n
            self.floors[self.floor]["grid"] = [[Tile() for _ in range(n)] for _ in range(n)]
        else:
            gained = B.YIELD[part]
            self.grid()[self.x][self.y] = Tile()
        self.inventory[part] += gained
        return gained

    def _good_board(self, x, y):
        tile = self.grid()[x][y]
        return tile.part == "BOARD" and self.is_ready(tile) and not tile.faulty

    def _harvest_board_square(self):
        n = self.size()
        for k in range(n, 1, -1):
            for sx in range(max(0, self.x - k + 1), min(self.x, n - k) + 1):
                for sy in range(max(0, self.y - k + 1), min(self.y, n - k) + 1):
                    cells = [(sx + i, sy + j) for i in range(k) for j in range(k)]
                    if all(self._good_board(cx, cy) for cx, cy in cells):
                        for cx, cy in cells:
                            self.grid()[cx][cy] = Tile()
                        return k ** 3
        self.grid()[self.x][self.y] = Tile()
        return B.YIELD["BOARD"]

    def swap(self, direction):
        if direction not in DIRS:
            raise ValueError("swap() needs a direction: North, East, South or West")
        dx, dy = DIRS[direction]
        nx, ny = self.x + dx, self.y + dy
        n = self.size()
        if not (0 <= nx < n and 0 <= ny < n):
            return False
        g = self.grid()
        g[self.x][self.y], g[nx][ny] = g[nx][ny], g[self.x][self.y]
        return True

    def gpu_grid_sorted(self):
        g, n = self.grid(), self.size()
        if not all(g[x][y].part == "GPU" and self.is_ready(g[x][y]) for x in range(n) for y in range(n)):
            return False
        rows = all(g[x][y].score <= g[x + 1][y].score for y in range(n) for x in range(n - 1))
        cols = all(g[x][y].score <= g[x][y + 1].score for x in range(n) for y in range(n - 1))
        return rows and cols

    # ---------------------------------------------------------------- lift + orders
    def goto_floor(self, name):
        if name not in self.floors:
            return False
        self.floor = name
        self.x %= self.size()
        self.y %= self.size()
        return True

    def new_order(self):
        kinds = min(5, 2 + self.orders_done // 3)
        parts = self.rng.sample(list(B.ORDER_BASE), kinds)
        scale = 1 + self.orders_done // 4
        self.order = {p: B.ORDER_BASE[p] * self.rng.randint(1, 2) * scale for p in parts}

    def assemble(self):
        if self.floor != "ASSEMBLY" or not self.order:
            return False
        if any(self.inventory[p] < n for p, n in self.order.items()):
            return False
        for p, n in self.order.items():
            self.inventory[p] -= n
        self.inventory["COMPUTER"] += 1
        self.orders_done += 1
        self.new_order()
        return True
```

- [ ] **Step 4: Run the tests to check they pass**

Run: `npm run test:py`
Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "v2: CPU/SSD/motherboard/GPU floor rules, lift and assembly orders"
```

---

### Task 4: The upgrade tree

**Files:**
- Create: `src/python/game/unlocks.py`
- Test: `tests/test_game.py` (add `UnlockTests`)

**Interfaces:**
- Consumes: `World` (Task 3).
- Produces:
  - `@dataclass Unlock(id, title, cost: dict, requires: tuple = (), floor: str|None = None, grid: tuple[str,int]|None = None, speed: int|None = None, windows: int = 0, summary: str = "", help: str|None = None)`
  - `UNLOCKS: list[Unlock]`, `BY_ID: dict[str, Unlock]`
  - `buy(world, unlock_id) -> tuple[bool, str]`
  - `windows_allowed(world) -> int` (1 + sum of bought `windows`)
  - `tree_json() -> list[dict]` (fields: id, title, cost, requires, summary, help, kind, windows), where kind ∈ `"feature" | "floor" | "grid" | "speed" | "other"`
- Feature unlock ids used by gating (Task 5): `loops, variables, conditionals, for_loops, positions, functions, lists, strings, sets, dicts, comprehensions, hof, modules, exceptions, classes`. Floor unlock ids: `floor_cpu, floor_ssd, floor_board, floor_gpu, floor_assembly`. Also `turbo`, `speed1`–`speed5`, and grid ids `grid_<floor lower>_<size>`.

- [ ] **Step 1: Write the failing tests**

```python
from game import unlocks as U  # noqa: E402


class UnlockTests(unittest.TestCase):
    def test_every_requirement_exists_and_tree_is_acyclic(self):
        seen = set()
        for u in U.UNLOCKS:  # list order must already be a valid buying order
            for r in u.requires:
                self.assertIn(r, seen, f"{u.id} requires {r}, which must come earlier in UNLOCKS")
            seen.add(u.id)

    def test_buy_pays_and_applies(self):
        w = World()
        w.inventory["RAM"] = 100
        ok, _ = U.buy(w, "loops")
        self.assertTrue(ok)
        self.assertIn("loops", w.unlocks)
        self.assertEqual(w.inventory["RAM"], 100 - U.BY_ID["loops"].cost["RAM"])

    def test_buy_refuses_missing_prereq_money_or_repeat(self):
        w = World()
        self.assertFalse(U.buy(w, "loops")[0])               # can't afford
        w.inventory["RAM"] = 10_000
        self.assertFalse(U.buy(w, "conditionals")[0])        # missing prerequisite
        self.assertTrue(U.buy(w, "loops")[0])
        self.assertFalse(U.buy(w, "loops")[0])               # already bought
        self.assertFalse(U.buy(w, "nope")[0])

    def test_floor_grid_speed_effects(self):
        w = World()
        w.inventory.update(RAM=100_000, CPU=100_000)
        for uid in ["loops", "variables", "conditionals", "floor_cpu", "speed1", "grid_ram_4"]:
            self.assertTrue(U.buy(w, uid)[0], uid)
        self.assertIn("CPU", w.floors)
        self.assertEqual(w.size("RAM"), 4)
        self.assertEqual(w.speed_level, 1)

    def test_tree_json_is_plain_data(self):
        import json
        data = json.loads(json.dumps(U.tree_json()))
        self.assertEqual(len(data), len(U.UNLOCKS))
        self.assertEqual({d["kind"] for d in data} >= {"feature", "floor", "grid", "speed"}, True)
```

- [ ] **Step 2: Run them to check they fail**

Run: `npm run test:py`
Expected: FAIL with `ModuleNotFoundError: No module named 'game.unlocks'`

- [ ] **Step 3: Implement `unlocks.py`**

```python
"""The upgrade tree. List order is a valid buying order (every requirement comes earlier)."""
from dataclasses import dataclass

from . import balance as B


@dataclass
class Unlock:
    id: str
    title: str
    cost: dict
    requires: tuple = ()
    floor: str | None = None
    grid: tuple | None = None
    speed: int | None = None
    windows: int = 0
    summary: str = ""
    help: str | None = None

    @property
    def kind(self):
        if self.floor:
            return "floor"
        if self.grid:
            return "grid"
        if self.speed:
            return "speed"
        return "feature" if self.help and not self.help.startswith("floor_") else "other"


def F(id, title, cost, requires=(), summary=""):
    """A Python-feature unlock with its own help page."""
    return Unlock(id, title, cost, tuple(requires), summary=summary, help=id)


def FLOOR(id, floor, title, cost, requires, summary):
    return Unlock(id, title, cost, tuple(requires), floor=floor, summary=summary, help=id)


def SPEED(level, cost, requires):
    return Unlock(f"speed{level}", f"Drone Speed {level}", cost, tuple(requires), speed=level,
                  summary=f"The drone works x{B.SPEEDS[level]} as fast in real time.")


UNLOCKS = [
    F("loops", "Loops", {"RAM": 5}, summary="while loops (and wait()) so the drone can keep working forever."),
    SPEED(1, {"RAM": 15}, ["loops"]),
    F("variables", "Variables & Operators", {"RAM": 20}, ["loops"],
      "Store values, do maths and compare things. Also num_items()."),
    F("conditionals", "Conditionals", {"RAM": 40}, ["variables"],
      "if / elif / else, plus can_harvest() and get_part()."),
    FLOOR("floor_cpu", "CPU", "CPU Floor", {"RAM": 60}, ["conditionals"],
          "Open the CPU floor. place() chips and let them bake. Ride the lift with goto_floor()."),
    F("for_loops", "For Loops & range", {"RAM": 50, "CPU": 5}, ["floor_cpu"], "for loops, range(), break and continue."),
    F("positions", "Positions & Tuples", {"RAM": 60, "CPU": 10}, ["for_loops"],
      "get_pos() gives an (x, y) tuple. get_world_size() gives the grid size."),
    F("functions", "Functions", {"CPU": 25}, ["for_loops"], "def your own reusable routines."),
    SPEED(2, {"RAM": 100, "CPU": 20}, ["speed1", "floor_cpu"]),
    FLOOR("floor_ssd", "SSD", "SSD Floor", {"RAM": 150, "CPU": 50}, ["functions"],
          "SSDs cost RAM and CPUs to place, but pay out double."),
    F("lists", "Lists", {"SSD": 10}, ["floor_ssd"], "Lists, indexing, append/pop, len()."),
    F("strings", "Strings & f-strings", {"SSD": 10}, ["floor_ssd"], "String methods, slicing and f-strings."),
    SPEED(3, {"SSD": 40}, ["speed2", "floor_ssd"]),
    FLOOR("floor_board", "BOARD", "Motherboard Floor", {"SSD": 40}, ["lists"],
          "Motherboards merge into big boards... but some come out faulty. is_faulty()!"),
    F("sets", "Sets", {"BOARD": 10}, ["floor_board"], "Collections with no duplicates."),
    F("dicts", "Dictionaries", {"BOARD": 15}, ["floor_board"], "Look things up by key."),
    F("comprehensions", "Comprehensions & lambda", {"BOARD": 30}, ["lists"], "Build lists in one line."),
    F("hof", "Higher-order Functions", {"BOARD": 40}, ["comprehensions", "functions"], "map, filter, sorted with key=."),
    SPEED(4, {"BOARD": 60}, ["speed3", "floor_board"]),
    FLOOR("floor_gpu", "GPU", "GPU Floor", {"BOARD": 60}, ["dicts"],
          "GPU chips have scores. Sort the whole grid for a huge bonus: measure() and swap()."),
    Unlock("modules", "Modules", {"GPU": 20}, ("floor_gpu",), windows=3, help="modules",
           summary="Up to 4 code windows that import each other, plus import math / random."),
    F("exceptions", "Exceptions", {"GPU": 30}, ["floor_gpu"], "try / except / finally and raise."),
    SPEED(5, {"GPU": 150}, ["speed4", "floor_gpu"]),
    FLOOR("floor_assembly", "ASSEMBLY", "Final Assembly", {"GPU": 100}, ["exceptions"],
          "Fill customer orders to build complete computers."),
    F("classes", "Classes", {"COMPUTER": 1}, ["floor_assembly"], "Design your own objects."),
    Unlock("turbo", "Turbo", {"COMPUTER": 2}, ("floor_assembly",), summary="A max-speed mode with no animation."),
]

GRID_BASE = {"RAM": 20, "CPU": 10, "SSD": 10, "BOARD": 8, "GPU": 20}
FLOOR_UNLOCK = {"RAM": "loops", "CPU": "floor_cpu", "SSD": "floor_ssd", "BOARD": "floor_board", "GPU": "floor_gpu"}

for _floor, _base in GRID_BASE.items():
    for _size in range(B.START_SIZE + 1, B.MAX_SIZE + 1):
        _prev = FLOOR_UNLOCK[_floor] if _size == B.START_SIZE + 1 else f"grid_{_floor.lower()}_{_size - 1}"
        UNLOCKS.append(Unlock(f"grid_{_floor.lower()}_{_size}", f"{_floor.title()} Grid {_size}x{_size}",
                              {_floor: _base * 2 ** (_size - B.START_SIZE - 1)}, (_prev,), grid=(_floor, _size),
                              summary=f"Make the {_floor} floor {_size}x{_size}."))

BY_ID = {u.id: u for u in UNLOCKS}


def buy(world, unlock_id):
    u = BY_ID.get(unlock_id)
    if u is None:
        return False, f"There's no upgrade called {unlock_id!r}."
    if u.id in world.unlocks:
        return False, f"You already own {u.title}."
    missing = [BY_ID[r].title for r in u.requires if r not in world.unlocks]
    if missing:
        return False, f"{u.title} needs {', '.join(missing)} first."
    short = {p: n - world.inventory.get(p, 0) for p, n in u.cost.items() if world.inventory.get(p, 0) < n}
    if short:
        return False, "Not enough parts: need " + ", ".join(f"{n} more {p}" for p, n in short.items()) + "."
    for p, n in u.cost.items():
        world.inventory[p] -= n
    world.unlocks.add(u.id)
    if u.floor:
        world.open_floor(u.floor)
    if u.grid:
        world.resize(*u.grid)
    if u.speed:
        world.speed_level = max(world.speed_level, u.speed)
    return True, f"Unlocked {u.title}!"


def windows_allowed(world):
    return 1 + sum(BY_ID[u].windows for u in world.unlocks if u in BY_ID)


def tree_json():
    return [{"id": u.id, "title": u.title, "cost": u.cost, "requires": list(u.requires),
             "summary": u.summary, "help": u.help, "kind": u.kind, "windows": u.windows} for u in UNLOCKS]
```

Note: grid unlocks need their floor, and `grid_ram_*` is appended after `loops`, so list order stays a valid buying order. The test checks this. If it fails because a floor unlock appears after a grid entry, that's impossible here, because all grids are appended at the end.

- [ ] **Step 4: Run the tests to check they pass**

Run: `npm run test:py`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "v2: upgrade tree with floors, grid sizes, speeds and Python features"
```

---

### Task 5: Feature gating (locked Python features can't run)

**Files:**
- Create: `src/python/game/gating.py`
- Test: `tests/test_game.py` (add `GatingTests`)

**Interfaces:**
- Consumes: `unlocks.BY_ID` (for titles).
- Produces:
  - `API_UNLOCK: dict[str, str|None]` (player API name → unlock id; `None` means available from the start)
  - `ALLOWED_STDLIB = {"math", "random"}`
  - `check(source: str, unlocked: set[str], filename: str, user_modules: set[str]) -> list[str]` returning friendly problem lines (empty = OK). A syntax error returns a one-item list with the friendly syntax error.

- [ ] **Step 1: Write the failing tests**

```python
from game.gating import check  # noqa: E402


class GatingTests(unittest.TestCase):
    def test_start_code_is_allowed(self):
        self.assertEqual(check("# hi\nharvest()\nmove(East)\nprint('x')\n", set(), "main.py", set()), [])

    def test_locked_while_is_reported_with_line_and_title(self):
        problems = check("harvest()\nwhile True:\n    harvest()\n", set(), "main.py", set())
        self.assertEqual(len(problems), 1)
        self.assertIn("Line 2", problems[0])
        self.assertIn("Loops", problems[0])

    def test_unlocked_while_passes(self):
        self.assertEqual(check("while True:\n    harvest()\n", {"loops"}, "main.py", set()), [])

    def test_locked_api_function(self):
        problems = check("while True:\n    if can_harvest():\n        harvest()\n", {"loops"}, "main.py", set())
        self.assertTrue(any("Conditionals" in p for p in problems))

    def test_locked_builtin(self):
        problems = check("for i in range(3):\n    harvest()\n", {"loops", "for_loops"}, "main.py", set())
        self.assertEqual(problems, [])
        problems = check("x = len([1])\n", {"variables"}, "main.py", set())
        self.assertTrue(any("Lists" in p for p in problems))

    def test_forbidden_names_and_dunders(self):
        self.assertTrue(check("open('x')\n", set(), "main.py", set()))
        self.assertTrue(check("harvest.__globals__\n", set(), "main.py", set()))

    def test_imports(self):
        all_on = {"modules", "variables"}
        self.assertEqual(check("import math\nimport helpers\n", all_on, "main.py", {"helpers"}), [])
        self.assertTrue(check("import os\n", all_on, "main.py", set()))
        self.assertTrue(check("import helpers\n", {"variables"}, "main.py", {"helpers"}))  # modules locked

    def test_other_file_names_itself(self):
        problems = check("while True:\n    pass\n", set(), "helpers.py", set())
        self.assertIn("helpers.py line 1", problems[0])

    def test_cannot_swallow_stop(self):
        on = {"exceptions", "loops"}
        self.assertTrue(check("try:\n    harvest()\nexcept:\n    pass\n", on, "main.py", set()))
        self.assertTrue(check("try:\n    harvest()\nexcept BaseException:\n    pass\n", on, "main.py", set()))
        self.assertEqual(check("try:\n    harvest()\nexcept Exception:\n    pass\n", on, "main.py", set()), [])

    def test_syntax_error_is_friendly(self):
        problems = check("harvest(\n", set(), "main.py", set())
        self.assertIn("SyntaxError", problems[0])
```

- [ ] **Step 2: Run them to check they fail**

Run: `npm run test:py`
Expected: FAIL with `ModuleNotFoundError: No module named 'game.gating'`

- [ ] **Step 3: Implement `gating.py`**

```python
"""Before a program runs, walk its syntax tree and refuse anything the player hasn't unlocked yet."""
import ast

from .errors import friendly_error
from .unlocks import BY_ID

NODE_FEATURE = {
    ast.While: ("loops", "while loops"), ast.Break: ("loops", "break"), ast.Continue: ("loops", "continue"),
    ast.Assign: ("variables", "variables"), ast.AugAssign: ("variables", "variables"),
    ast.AnnAssign: ("variables", "variables"), ast.BinOp: ("variables", "maths operators"),
    ast.UnaryOp: ("variables", "operators"), ast.Compare: ("variables", "comparisons"),
    ast.BoolOp: ("variables", "and / or"),
    ast.If: ("conditionals", "if statements"), ast.IfExp: ("conditionals", "if expressions"),
    ast.For: ("for_loops", "for loops"),
    ast.FunctionDef: ("functions", "def"), ast.Return: ("functions", "return"),
    ast.Global: ("functions", "global"), ast.Nonlocal: ("functions", "nonlocal"),
    ast.List: ("lists", "lists"), ast.Subscript: ("lists", "[ ] indexing"),
    ast.Tuple: ("positions", "tuples"),
    ast.Dict: ("dicts", "dictionaries"), ast.Set: ("sets", "sets"),
    ast.JoinedStr: ("strings", "f-strings"),
    ast.ListComp: ("comprehensions", "list comprehensions"), ast.SetComp: ("comprehensions", "set comprehensions"),
    ast.DictComp: ("comprehensions", "dict comprehensions"), ast.GeneratorExp: ("comprehensions", "generator expressions"),
    ast.Lambda: ("comprehensions", "lambda"),
    ast.Import: ("modules", "import"), ast.ImportFrom: ("modules", "import"),
    ast.Try: ("exceptions", "try / except"), ast.Raise: ("exceptions", "raise"),
    ast.ClassDef: ("classes", "class"),
}

BUILTIN_UNLOCK = {
    "range": "for_loops", "enumerate": "lists", "zip": "lists", "len": "lists", "list": "lists", "sum": "lists",
    "reversed": "lists", "any": "lists", "all": "lists", "tuple": "positions", "dict": "dicts", "set": "sets",
    "str": "strings", "sorted": "hof", "map": "hof", "filter": "hof", "int": "variables", "float": "variables",
    "abs": "variables", "min": "variables", "max": "variables", "round": "variables", "bool": "variables",
    "type": "variables", "isinstance": "classes", "super": "classes", "Exception": "exceptions",
    "ValueError": "exceptions", "KeyError": "exceptions", "IndexError": "exceptions", "TypeError": "exceptions",
    "ZeroDivisionError": "exceptions",
}

API_UNLOCK = {
    "harvest": None, "move": None, "print": None, "North": None, "East": None, "South": None, "West": None,
    "Part": None, "wait": "loops", "num_items": "variables", "can_harvest": "conditionals",
    "get_part": "conditionals", "place": "floor_cpu", "goto_floor": "floor_cpu", "get_floor": "floor_cpu",
    "Floor": "floor_cpu", "get_pos": "positions", "get_world_size": "positions", "is_faulty": "floor_board",
    "FaultyBoardError": "floor_board", "measure": "floor_gpu", "swap": "floor_gpu", "get_order": "floor_assembly",
    "assemble": "floor_assembly",
}

# BaseException / KeyboardInterrupt / SystemExit are blocked so a program can't swallow the Stop button.
FORBIDDEN = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "vars", "input", "breakpoint",
             "exit", "quit", "help", "getattr", "setattr", "delattr", "memoryview", "__builtins__",
             "BaseException", "KeyboardInterrupt", "SystemExit"}
ALLOWED_DUNDERS = {"__init__", "__str__", "__repr__", "__name__", "__eq__", "__lt__"}
ALLOWED_STDLIB = {"math", "random"}
UNSUPPORTED = (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith, ast.Yield, ast.YieldFrom, ast.With)


def _where(filename, line):
    return f"Line {line}" if filename == "main.py" else f"{filename} line {line}"


def _locked(node, what, unlock_id):
    title = BY_ID[unlock_id].title
    return node.lineno, f"you haven't unlocked {what} yet. Find \u201c{title}\u201d in the Upgrades tree."


def check(source, unlocked, filename, user_modules):
    try:
        tree = ast.parse(source, filename)
    except SyntaxError as exc:
        return [friendly_error(exc, {filename})]
    found = set()   # (line, message): the same problem on the same line is reported once
    for node in ast.walk(tree):
        if isinstance(node, UNSUPPORTED):
            found.add((node.lineno, "ByteWorks doesn't support that kind of statement."))
            continue
        feature = NODE_FEATURE.get(type(node))
        if feature and feature[0] not in unlocked:
            found.add(_locked(node, feature[1], feature[0]))
        if isinstance(node, ast.Name):
            name = node.id
            if name in FORBIDDEN:
                found.add((node.lineno, f"{name} isn't available in ByteWorks."))
            elif API_UNLOCK.get(name) and API_UNLOCK[name] not in unlocked:
                found.add(_locked(node, name, API_UNLOCK[name]))
            elif name in BUILTIN_UNLOCK and BUILTIN_UNLOCK[name] not in unlocked:
                found.add(_locked(node, f"{name}()", BUILTIN_UNLOCK[name]))
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            found.add((node.lineno, "name the error you expect, e.g. except FaultyBoardError: (a bare except: would "
                                    "also catch the Stop button)."))
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr not in ALLOWED_DUNDERS:
            found.add((node.lineno, f"{node.attr} isn't available in ByteWorks."))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in names:
                if name not in ALLOWED_STDLIB and name not in user_modules:
                    found.add((node.lineno, f"you can only import math, random or your own code windows, not {name!r}."))
    return [f"{_where(filename, line)}: {msg}" for line, msg in sorted(found)]
```

- [ ] **Step 4: Run the tests to check they pass**

Run: `npm run test:py`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "v2: AST feature gating for locked Python features"
```

---

### Task 6: Player API and program runner

**Files:**
- Create: `src/python/game/api.py`, `src/python/game/runner.py`, `src/python/game/sandbox.py`
- Test: `tests/test_game.py` (add `RunnerTests`, `SandboxTests`)

**Interfaces:**
- Consumes: `World` (Task 3), `gating.check`, `gating.FORBIDDEN`, `gating.ALLOWED_STDLIB` (Task 5), `friendly_error` (Task 1), `balance`.
- Produces:
  - `api.StopRun(BaseException)`, `api.Part`, `api.Floor` (string constants), `api.Api(world, pace=None, on_change=None, on_print=None, max_ticks=None)` with `.namespace() -> dict`
  - Hooks contract: `pace(ms: float)` blocks for `ms` of real time at UI speed x1. `on_change(anim_ms: float)` is called after every non-sensing action (before pacing) and once with `0` when the run ends. `on_print(text: str)`.
  - `runner.run_program(world, files: dict[str,str], entry="main.py", pace=None, on_change=None, on_print=None, max_ticks=None) -> dict` returning `{"ok": bool, "stopped": bool, "error"?: str}`
  - `sandbox.run_snippet(code: str) -> dict` returning `{"stdout": str, "error": str|None}`

Player-visible API (names from the spec). Sensing calls cost `ACTION_TICKS["sense"]` and never pace:

| name | behaviour |
|---|---|
| `harvest()` | `world.harvest()`. Returns True if anything was gained. Costs `harvest` |
| `move(d)` | `world.move(d)`, costs `move` |
| `print(*values, sep=" ")` | `on_print(text)`, costs `print` |
| `wait(ticks)` | int ≥ 0, costs `ticks` |
| `num_items(part)` | sense. `ValueError` if the part is unknown |
| `can_harvest()`, `get_part()`, `is_faulty()`, `measure()`, `get_pos()` → `(x, y)`, `get_world_size()`, `get_floor()`, `get_order()` → dict copy or None | sense |
| `place(part)` | costs `place`. `ValueError` for an unknown part |
| `swap(d)` | costs `swap` |
| `goto_floor(f)` | costs `goto_floor`. `ValueError` for an unknown floor name |
| `assemble()` | costs `assemble` |
| constants | `North East South West`, `Part.RAM … Part.COMPUTER`, `Floor.RAM … Floor.ASSEMBLY`, `FaultyBoardError` |

- [ ] **Step 1: Write the failing tests**

```python
from game.runner import run_program  # noqa: E402
from game.sandbox import run_snippet  # noqa: E402
from game import unlocks as U2  # noqa: E402


def with_prereqs(ids):
    wanted = set()
    todo = [u.id for u in U2.UNLOCKS] if "all" in ids else list(ids)
    while todo:
        uid = todo.pop()
        if uid not in wanted:
            wanted.add(uid)
            todo.extend(U2.BY_ID[uid].requires)
    return wanted


def unlocked_world(*ids, **inventory):
    """A world that owns the given unlocks (plus everything they require), with an empty inventory."""
    w = World(seed=5)
    w.inventory.update({p: 10**6 for p in w.inventory})
    wanted = with_prereqs(ids)
    for uid in [u.id for u in U2.UNLOCKS]:   # list order is a valid buying order
        if uid in wanted:
            assert U2.buy(w, uid)[0], uid
    w.inventory.update({p: 0 for p in w.inventory})
    w.inventory.update(inventory)
    return w


class RunnerTests(unittest.TestCase):
    def test_start_program_harvests_and_spends_ticks(self):
        w = World()
        r = run_program(w, {"main.py": "harvest()\nmove(East)\nharvest()\n"})
        self.assertEqual(r, {"ok": True, "stopped": False})
        self.assertEqual(w.inventory["RAM"], 2)
        self.assertEqual(w.clock, 2 * B.ACTION_TICKS["harvest"] + B.ACTION_TICKS["move"])

    def test_locked_feature_does_not_run(self):
        w = World()
        r = run_program(w, {"main.py": "harvest()\nwhile True:\n    harvest()\n"})
        self.assertFalse(r["ok"])
        self.assertIn("Line 2", r["error"])
        self.assertEqual(w.clock, 0)

    def test_print_goes_to_console_hook(self):
        out = []
        run_program(World(), {"main.py": "print('hello', 'drone')\n"}, on_print=out.append)
        self.assertEqual(out, ["hello drone"])

    def test_tick_budget_stops_forever_loop(self):
        w = unlocked_world("loops")
        r = run_program(w, {"main.py": "while True:\n    harvest()\n    move(North)\n"}, max_ticks=5000)
        self.assertEqual(r, {"ok": True, "stopped": True})
        self.assertGreater(w.inventory["RAM"], 0)
        self.assertGreaterEqual(w.clock, 5000)

    def test_stop_cannot_be_caught_by_except_exception(self):
        w = unlocked_world("all")
        code = "while True:\n    try:\n        harvest()\n    except Exception:\n        pass\n"
        self.assertTrue(run_program(w, {"main.py": code}, max_ticks=2000)["stopped"])

    def test_keyboard_interrupt_from_pace_means_stopped(self):
        def pace(ms):
            raise KeyboardInterrupt
        r = run_program(unlocked_world("loops"), {"main.py": "while True:\n    harvest()\n"}, pace=pace)
        self.assertEqual(r, {"ok": True, "stopped": True})

    def test_hooks_get_real_time_scaled_by_speed(self):
        w = unlocked_world("loops", "speed1")
        paced, changed = [], []
        run_program(w, {"main.py": "harvest()\n"}, pace=paced.append, on_change=changed.append)
        want = B.ACTION_TICKS["harvest"] * B.MS_PER_TICK / B.SPEEDS[1]
        self.assertEqual(paced, [want])
        self.assertEqual(changed, [want, 0])

    def test_uncaught_faulty_board_is_friendly(self):
        w = unlocked_world("floor_board")
        w.goto_floor("BOARD")
        w.grid()[0][0] = Tile("BOARD", 0, True, None, 0)
        r = run_program(w, {"main.py": "move(East)\nmove(West)\nharvest()\n"})
        self.assertFalse(r["ok"])
        self.assertTrue(r["error"].startswith("Line 3: FaultyBoardError"), r["error"])
        self.assertIn("is_faulty()", r["error"])

    def test_faulty_board_can_be_caught(self):
        w = unlocked_world("all")
        w.goto_floor("BOARD")
        w.grid()[0][0] = Tile("BOARD", 0, True, None, 0)
        code = "try:\n    harvest()\nexcept FaultyBoardError:\n    print('caught')\n"
        out = []
        self.assertTrue(run_program(w, {"main.py": code}, on_print=out.append)["ok"])
        self.assertEqual(out, ["caught"])

    def test_import_own_file(self):
        w = unlocked_world("all")
        files = {"main.py": "import helpers\nhelpers.sweep(2)\n",
                 "helpers.py": "def sweep(n):\n    for i in range(n):\n        harvest()\n        move(North)\n"}
        self.assertTrue(run_program(w, files)["ok"])
        self.assertEqual(w.inventory["RAM"], 2)

    def test_locked_feature_in_imported_file(self):
        w = unlocked_world("modules")   # modules + prerequisites, but NOT exceptions
        files = {"main.py": "import helpers\n", "helpers.py": "x = 1\ntry:\n    harvest()\nexcept Exception:\n    pass\n"}
        r = run_program(w, files)
        self.assertFalse(r["ok"])
        self.assertIn("helpers.py line 2", r["error"])
        self.assertEqual(w.clock, 0)

    def test_bad_arguments_are_explained(self):
        r = run_program(World(), {"main.py": "move('Up')\n"})
        self.assertIn("Line 1: ValueError", r["error"])
        self.assertIn("North, East, South or West", r["error"])


class SandboxTests(unittest.TestCase):
    def test_snippet_output_and_errors(self):
        self.assertEqual(run_snippet("print(1 + 2)"), {"stdout": "3\n", "error": None})
        self.assertTrue(run_snippet("print(nope)")["error"].startswith("Line 1: NameError"))
```

- [ ] **Step 2: Run them to check they fail**

Run: `npm run test:py`
Expected: FAIL with `ModuleNotFoundError: No module named 'game.runner'`

- [ ] **Step 3: Implement `api.py`**

```python
"""The functions a player's program can call. Each action changes the world, adds game ticks,
tells the screen to redraw, then waits in real time so the player can watch it happen."""
from . import balance as B
from .world import DIRS, FLOORS, PARTS, FaultyBoardError


class StopRun(BaseException):
    """Ends a run early (tick budget used up). BaseException, so `except Exception` can't catch it."""


class Part:
    RAM, CPU, SSD, BOARD, GPU, COMPUTER = PARTS


class Floor:
    RAM, CPU, SSD, BOARD, GPU, ASSEMBLY = FLOORS


class Api:
    def __init__(self, world, pace=None, on_change=None, on_print=None, max_ticks=None):
        self.world = world
        self.pace = pace
        self.on_change = on_change
        self.on_print = on_print or (lambda text: None)
        self.limit = None if max_ticks is None else world.clock + max_ticks

    def _spend(self, action, ticks=None):
        ticks = B.ACTION_TICKS[action] if ticks is None else ticks
        self.world.clock += ticks
        if action != "sense":
            ms = ticks * B.MS_PER_TICK / B.SPEEDS[self.world.speed_level]
            if self.on_change:
                self.on_change(ms)
            if self.pace:
                self.pace(ms)
        if self.limit is not None and self.world.clock >= self.limit:
            raise StopRun()

    def _sense(self, value):
        self._spend("sense")
        return value

    @staticmethod
    def _check(value, allowed, what):
        if value not in allowed:
            raise ValueError(f"{what} must be one of: {', '.join(allowed)}")

    # ---- actions
    def harvest(self):
        try:
            return self.world.harvest() > 0
        finally:
            self._spend("harvest")

    def move(self, direction):
        self.world.move(direction)
        self._spend("move")
        return True

    def print(self, *values, sep=" "):
        self.on_print(sep.join(str(v) for v in values))
        self._spend("print")

    def wait(self, ticks):
        if not isinstance(ticks, int) or ticks < 0:
            raise ValueError("wait() needs a whole number of ticks, like wait(100)")
        self._spend("move", ticks)   # any non-sense action name works: it animates and paces

    def place(self, part):
        self._check(part, PARTS[:-1], "place()'s part")
        ok = self.world.place(part)
        self._spend("place")
        return ok

    def swap(self, direction):
        ok = self.world.swap(direction)
        self._spend("swap")
        return ok

    def goto_floor(self, floor):
        self._check(floor, FLOORS, "goto_floor()'s floor")
        ok = self.world.goto_floor(floor)
        self._spend("goto_floor")
        return ok

    def assemble(self):
        ok = self.world.assemble()
        self._spend("assemble")
        return ok

    # ---- sensing
    def num_items(self, part):
        self._check(part, PARTS, "num_items()'s part")
        return self._sense(self.world.inventory[part])

    def can_harvest(self):
        return self._sense(self.world.can_harvest())

    def get_part(self):
        return self._sense(self.world.get_part())

    def is_faulty(self):
        return self._sense(self.world.is_faulty())

    def measure(self):
        return self._sense(self.world.measure())

    def get_pos(self):
        return self._sense((self.world.x, self.world.y))

    def get_world_size(self):
        return self._sense(self.world.size())

    def get_floor(self):
        return self._sense(self.world.floor)

    def get_order(self):
        return self._sense(dict(self.world.order) if self.world.order else None)

    def namespace(self):
        ns = {name: getattr(self, name) for name in (
            "harvest", "move", "print", "wait", "place", "swap", "goto_floor", "assemble", "num_items",
            "can_harvest", "get_part", "is_faulty", "measure", "get_pos", "get_world_size", "get_floor", "get_order")}
        ns.update({d: d for d in DIRS})
        ns.update(Part=Part, Floor=Floor, FaultyBoardError=FaultyBoardError)
        return ns
```

Note on `wait`: `_spend("move", ticks)` uses the explicit tick count. The action name only decides that it is not a sensing call.

- [ ] **Step 4: Implement `runner.py`**

```python
"""Run the player's program: check what's unlocked, give it the drone API, and explain any errors."""
import builtins
import types

from .api import Api, StopRun
from .errors import friendly_error
from .gating import ALLOWED_STDLIB, FORBIDDEN, check

MAX_PROBLEMS = 6


class GateError(Exception):
    """A code window imported by the program uses something locked."""


def run_program(world, files, entry="main.py", pace=None, on_change=None, on_print=None, max_ticks=None):
    if entry not in files:
        return {"ok": False, "stopped": False, "error": f"There's no code window called {entry}."}
    user_modules = {name[:-3] for name in files if name.endswith(".py") and name != entry}
    problems = check(files[entry], world.unlocks, entry, user_modules)
    if problems:
        return {"ok": False, "stopped": False, "error": "\n".join(problems[:MAX_PROBLEMS])}

    api = Api(world, pace, on_change, on_print, max_ticks)
    safe_builtins = {k: v for k, v in vars(builtins).items() if k not in FORBIDDEN}
    loaded = {}

    def gated_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in ALLOWED_STDLIB:
            return __import__(name)
        if name not in user_modules:
            raise ModuleNotFoundError(f"No code window called {name!r}")
        if name not in loaded:
            filename = f"{name}.py"
            found = check(files[filename], world.unlocks, filename, user_modules)
            if found:
                raise GateError("\n".join(found[:MAX_PROBLEMS]))
            module = types.ModuleType(name)
            module.__dict__.update(api.namespace())
            module.__dict__["__builtins__"] = safe_builtins
            loaded[name] = module
            exec(compile(files[filename], filename, "exec"), module.__dict__)
        return loaded[name]

    safe_builtins["__import__"] = gated_import
    safe_builtins["print"] = api.print
    namespace = api.namespace()
    namespace.update(__builtins__=safe_builtins, __name__="__main__")
    user_files = {entry} | {f"{m}.py" for m in user_modules}
    try:
        exec(compile(files[entry], entry, "exec"), namespace)
        return {"ok": True, "stopped": False}
    except (KeyboardInterrupt, StopRun):
        return {"ok": True, "stopped": True}
    except GateError as exc:
        return {"ok": False, "stopped": False, "error": str(exc)}
    except Exception as exc:  # the player's program crashed: explain it kindly
        return {"ok": False, "stopped": False, "error": friendly_error(exc, user_files)}
    finally:
        if on_change:
            on_change(0)
```

Every return path includes `"stopped"`, because the tests compare whole result dicts.

- [ ] **Step 5: Implement `sandbox.py`**

```python
"""Runs a help page's "Try it" example: plain Python, no drone, output captured."""
import contextlib
import io

from .errors import friendly_error

MAX_OUTPUT = 20_000


def run_snippet(code):
    out = io.StringIO()
    error = None
    try:
        compiled = compile(code, "main.py", "exec")
        with contextlib.redirect_stdout(out):
            exec(compiled, {"__name__": "__main__"})
    except Exception as exc:
        error = friendly_error(exc, {"main.py"})
    return {"stdout": out.getvalue()[:MAX_OUTPUT], "error": error}
```

- [ ] **Step 6: Run the tests to check they pass**

Run: `npm run test:py`
Expected: all pass. If `test_uncaught_faulty_board_is_friendly` reports a line inside `world.py`, check that `friendly_error` is given `user_files` containing `"main.py"` and that the program is compiled with the filename `"main.py"`.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "v2: player API, gated program runner and snippet sandbox"
```

---

### Task 7: Reference bots play the whole game (completability + balance)

**Files:**
- Create: `tests/bots/s0_start.py`, `s1_loop.py`, `s2_cpu.py`, `s3_ssd.py`, `s4_board.py`, `s5_gpu.py`, `s6_assembly.py`
- Create: `tests/test_progress.py`
- Modify (tuning only, if needed): `src/python/game/balance.py`, and costs in `src/python/game/unlocks.py`

**Interfaces:**
- Consumes: `run_program(..., max_ticks=)` (Task 6), `unlocks.buy/BY_ID` (Task 4), `balance.WIN_COMPUTERS`.
- Produces: a test that fails if the game can't be finished, or takes more than `MAX_TOTAL` ticks. Each bot only uses features unlocked at its stage, and gating enforces this automatically.

- [ ] **Step 1: Write the bots**

`tests/bots/s0_start.py` (nothing unlocked):
```python
harvest()
move(North)
harvest()
move(North)
harvest()
move(East)
harvest()
move(South)
harvest()
move(South)
harvest()
move(East)
harvest()
move(North)
harvest()
move(North)
harvest()
move(East)
```

`tests/bots/s1_loop.py` (loops):
```python
while True:
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
    move(East)
```

`tests/bots/s2_cpu.py` (+ variables, conditionals, CPU floor):
```python
while True:
    goto_floor(Floor.CPU)
    i = 0
    while i < 9:
        if can_harvest():
            harvest()
        if get_part() == None:
            place(Part.CPU)
        move(North)
        i = i + 1
        if i % 3 == 0:
            move(East)
    goto_floor(Floor.RAM)
    i = 0
    while i < 9:
        harvest()
        move(North)
        i = i + 1
        if i % 3 == 0:
            move(East)
```

`tests/bots/s3_ssd.py` (+ for, positions, functions, SSD floor):
```python
def tend(part):
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            move(North)
        move(East)


while True:
    goto_floor(Floor.RAM)
    tend(Part.RAM)
    goto_floor(Floor.CPU)
    tend(Part.CPU)
    goto_floor(Floor.SSD)
    tend(Part.SSD)
```

`tests/bots/s4_board.py` (+ lists, motherboard floor):
```python
def tend(part):
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if get_part() == Part.BOARD and is_faulty():
                place(Part.BOARD)
            elif can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            move(North)
        move(East)


floors = [Floor.RAM, Floor.CPU, Floor.SSD, Floor.BOARD]
while True:
    for f in floors:
        goto_floor(f)
        tend(f)
```

`tests/bots/s5_gpu.py`: identical to `s4_board.py`, except the list is
`floors = [Floor.RAM, Floor.CPU, Floor.SSD, Floor.BOARD, Floor.GPU]`.

`tests/bots/s6_assembly.py`:
```python
def tend(part):
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if get_part() == Part.BOARD and is_faulty():
                place(Part.BOARD)
            elif can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            move(North)
        move(East)


floors = [Floor.RAM, Floor.CPU, Floor.SSD, Floor.BOARD, Floor.GPU]
while True:
    for f in floors:
        goto_floor(f)
        tend(f)
    goto_floor(Floor.ASSEMBLY)
    while assemble():
        pass
```

These bots are deliberately simple (no merging, no GPU sorting). If *they* can finish in time, a real player who learns the bonuses will be faster.

- [ ] **Step 2: Write the progression test**

`tests/test_progress.py`:
```python
"""Plays the whole game with the reference bots: proves it can be finished, and in a sensible time."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

from game import balance as B  # noqa: E402
from game import unlocks as U  # noqa: E402
from game.runner import run_program  # noqa: E402
from game.world import World  # noqa: E402

BOTS = Path(__file__).parent / "bots"
CHUNK = 20_000            # ticks per run before the test checks progress again
MAX_TOTAL = 6_000_000     # ~3.3 hours of drone time at speed x1

STAGES = [
    ("s0_start", ["loops"]),
    ("s1_loop", ["speed1", "variables", "conditionals", "floor_cpu"]),
    ("s2_cpu", ["for_loops", "positions", "functions", "speed2", "floor_ssd"]),
    ("s3_ssd", ["lists", "strings", "speed3", "grid_ram_4", "grid_cpu_4", "floor_board"]),
    ("s4_board", ["sets", "dicts", "comprehensions", "hof", "speed4", "floor_gpu"]),
    ("s5_gpu", ["modules", "exceptions", "speed5", "floor_assembly"]),
    ("s6_assembly", ["classes", "turbo"]),
]


def bot(name):
    return {"main.py": (BOTS / f"{name}.py").read_text()}


class ProgressionTest(unittest.TestCase):
    def farm_until(self, world, name, done):
        while not done():
            self.assertLess(world.clock, MAX_TOTAL, f"too slow / stuck at {name}: {world.inventory}")
            result = run_program(world, bot(name), max_ticks=CHUNK)
            self.assertTrue(result["ok"], f"{name} failed: {result.get('error')}")

    def test_game_can_be_finished(self):
        world = World(seed=3)
        for name, buys in STAGES:
            for uid in buys:
                cost = U.BY_ID[uid].cost
                self.farm_until(world, name, lambda: all(world.inventory[p] >= n for p, n in cost.items()))
                ok, message = U.buy(world, uid)
                self.assertTrue(ok, f"{name}: {message}")
        self.farm_until(world, "s6_assembly", lambda: world.inventory["COMPUTER"] >= B.WIN_COMPUTERS)
        hours = world.clock * B.MS_PER_TICK / 3_600_000
        print(f"\nReference bots finished in {world.clock:,} ticks (~{hours:.1f} h at x1)", file=sys.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run it**

Run: `python3 -m unittest tests.test_progress -v`
Expected: either PASS with a printed time, or FAIL naming the stage where it got stuck or ran too slowly.

- [ ] **Step 4: Tune the balance until it passes in 1.5–3.3 hours**

Only change numbers, in `balance.py` (`ORDER_BASE`, `GROW_TICKS`, `PLACE_COST`, `YIELD`) and the `cost` dicts in `unlocks.py`. Never change the bots to make it pass. Rules of thumb:
- Stuck at a stage while farming X: lower the cost in X of that stage's upgrades, or raise `YIELD[X]`.
- Final Assembly too slow: lower `ORDER_BASE`, especially GPU and BOARD.
- Finished in under 1.5 h: raise upgrade costs in the late stages.

After each change: `python3 -m unittest tests.test_progress -v`. Then run `npm run test:py` again, because world tests pin some numbers through `B.*` and should still pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "v2: reference bots prove the game can be finished; balance tuned"
```

---

### Task 8: Worker, live pacing and Stop (Pyodide bridge + GameRunner)

**Files:**
- Create: `src/python/game/worker_glue.py`, `src/engine/types.ts`, `src/engine/game.ts`
- Rewrite: `src/engine/python.worker.ts`
- Delete: `src/engine/runner.ts`
- Create: `public/coi-serviceworker.min.js` (copied from npm)
- Modify: `index.html`, `vite.config.ts`, `package.json` (dependency)

**Interfaces:**
- Consumes: `run_program`, `run_snippet`, `unlocks.buy`, `unlocks.tree_json`, `World.to_state/from_state`.
- Produces (TS, used by all UI tasks):
  ```ts
  // types.ts
  export type Tile = [part: string | null, readyAt: number, faulty: boolean, score: number | null, plantedAt: number];
  export interface FloorState { size: number; grid: Tile[][] }            // grid[x][y], y = 0 is South
  export interface WorldState {
    seed: number; clock: number; inventory: Record<string, number>; unlocks: string[]; speed_level: number;
    floors: Record<string, FloorState>; floor: string; x: number; y: number;
    order: Record<string, number> | null; orders_done: number; rng: unknown;
  }
  export interface UnlockInfo {
    id: string; title: string; cost: Record<string, number>; requires: string[]; summary: string;
    help: string | null; kind: "feature" | "floor" | "grid" | "speed" | "other"; windows: number;
  }
  export interface RunResult { ok: boolean; stopped: boolean; error?: string; state: WorldState }
  export interface BuyResult { ok: boolean; message: string; state: WorldState }
  export interface SnippetResult { stdout: string; error: string | null }
  export type RunnerStatus = "loading" | "ready" | "failed";
  ```
  ```ts
  // game.ts
  export class GameRunner {
    readonly isolated: boolean;
    latest: WorldState | null;
    running: boolean;
    onState?: (state: WorldState, animMs: number) => void;
    onPrint?: (text: string) => void;
    onStatus?: (status: RunnerStatus) => void;
    start(state: WorldState | null): void;
    setSpeed(multiplier: number): void;   // 1, 4, 16; 0 = turbo (no pacing)
    run(files: Record<string, string>, entry: string): Promise<RunResult>;
    stop(): void;
    buy(unlockId: string): Promise<BuyResult>;
    tree(): Promise<UnlockInfo[]>;
    snippet(code: string): Promise<SnippetResult>;
    newGame(): Promise<WorldState>;
  }
  ```
- Worker message protocol: main → worker `{id, type: "init"|"run"|"buy"|"tree"|"snippet"|"new", ...}`. Worker → main `{id, ok, result|error}` replies, plus unsolicited `{type: "state", state: string, animMs: number}` and `{type: "print", text: string}`.

- [ ] **Step 1: Write `worker_glue.py`**

```python
"""What the Pyodide worker calls. Holds the one World for this browser tab.

`bw_bridge` is a JavaScript module the worker registers before importing this file:
    bw_bridge.pace(ms)              block for ms of real time (already divided by drone speed)
    bw_bridge.state(json, anim_ms)  post the world to the page for drawing
    bw_bridge.out(text)             post a console line
"""
import json
import time

import bw_bridge

from . import sandbox, unlocks
from .runner import run_program
from .world import World

WORLD = None
_last_post = 0.0
POST_EVERY = 1 / 60   # never flood the page with more than ~60 redraws per second


def _state():
    return json.dumps(WORLD.to_state())


def _changed(anim_ms):
    global _last_post
    now = time.monotonic()
    if anim_ms == 0 or now - _last_post >= POST_EVERY:
        _last_post = now
        bw_bridge.state(_state(), anim_ms)


def init(state_json):
    global WORLD
    WORLD = World.from_state(json.loads(state_json)) if state_json else World(seed=int(time.time()) % 1_000_000)
    return _state()


def new_game():
    global WORLD
    WORLD = World(seed=int(time.time()) % 1_000_000)
    return _state()


def run(files_json, entry):
    result = run_program(WORLD, json.loads(files_json), entry,
                         pace=bw_bridge.pace, on_change=_changed, on_print=bw_bridge.out)
    result["state"] = WORLD.to_state()
    return json.dumps(result)


def buy(unlock_id):
    ok, message = unlocks.buy(WORLD, unlock_id)
    return json.dumps({"ok": ok, "message": message, "state": WORLD.to_state()})


def tree():
    return json.dumps(unlocks.tree_json())


def snippet(code):
    return json.dumps(sandbox.run_snippet(code))
```

- [ ] **Step 2: Rewrite `src/engine/python.worker.ts`**

```ts
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
    else if (type === "snippet") result = glue.snippet(e.data.code);
    else if (type === "new") result = glue.new_game();
    self.postMessage({ id, ok: true, result });
  } catch (err) {
    self.postMessage({ id, ok: false, error: String(err) });
  }
};
```

- [ ] **Step 3: Write `src/engine/types.ts`** with exactly the types in the Interfaces block above.

- [ ] **Step 4: Write `src/engine/game.ts`**

```ts
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
      this.setState(JSON.parse(json as string), 0);
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
      clearTimeout(this.watchdog);
    }
  }

  stop() {
    if (!this.running) return;
    if (this.interrupt && this.ctrl) {
      this.interrupt[0] = 2;                 // SIGINT: Python raises KeyboardInterrupt at the next bytecode
      Atomics.store(this.ctrl, 1, 1);
      Atomics.notify(this.ctrl, 1);          // wake a drone that's mid-action
      this.watchdog = setTimeout(() => this.restart(), STOP_WATCHDOG_MS);
    } else {
      this.restart();
    }
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
```

- [ ] **Step 5: Cross-origin isolation (dev, preview and GitHub Pages)**

```bash
npm i coi-serviceworker
mkdir -p public && cp node_modules/coi-serviceworker/coi-serviceworker.min.js public/
git rm -q src/engine/runner.ts
```

In `index.html`, put this line inside `<head>`, **before** any other script:
```html
<script src="coi-serviceworker.min.js"></script>
```

In `vite.config.ts`, add inside `defineConfig({...})`:
```ts
  server: { headers: { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp" } },
  preview: { headers: { "Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp" } },
```

In `src/app/styles.css`, delete the `@import url("https://fonts.googleapis.com/...")` line and change the font stacks to
`system-ui, "Segoe UI", Roboto, sans-serif` (body) and `ui-monospace, "Cascadia Code", Menlo, monospace` (`--mono`).
Under `require-corp`, cross-origin stylesheets without CORP headers get blocked.

- [ ] **Step 6: Temporary smoke page to prove live runs and Stop work**

Temporarily replace `src/main.tsx` with:
```tsx
import { game } from "./engine/game";

const pre = document.createElement("pre");
document.getElementById("app")!.append(pre);
const log = (s: string) => (pre.textContent += s + "\n");
game.onStatus = (s) => log("status: " + s);
game.onPrint = (t) => log("print: " + t);
game.onState = (s, ms) => log(`drone at (${s.x}, ${s.y}) RAM=${s.inventory.RAM} anim=${Math.round(ms)}ms`);
game.start(null);
(window as any).game = game;
log("isolated: " + game.isolated);
```

Run `npx vite --port 5317`. Open `http://localhost:5317/` in Chrome (new tab). Then run these in the page with the JavaScript tool, and check each expected result:
1. `await game.run({"main.py": "harvest()\nmove(East)\nprint('hi')"}, "main.py")` → `{ok: true, stopped: false}`, the log shows `print: hi`, and state lines arrive about 200 ms apart.
2. `await game.run({"main.py": "while True:\n    harvest()"}, "main.py")` → `ok: false`, and the error names Loops (locked).
3. Buy loops after farming: `game.latest.inventory.RAM` must be ≥ 5, so run program 1 a few times first. Then `await game.buy("loops")` → `ok: true`.
4. `const p = game.run({"main.py": "while True:\n    harvest()\n    move(North)"}, "main.py"); setTimeout(() => game.stop(), 1500); await p` → `{ok: true, stopped: true}`, and RAM kept increasing before the stop.
5. (Loops is owned after step 3.) `const q = game.run({"main.py": "while True:\n    pass"}, "main.py"); setTimeout(() => game.stop(), 1000); await q` → `{ok: true, stopped: true}`. A program with no drone actions can still be stopped (Review Focus).
6. `game.isolated` is `true` under `vite` dev (headers). Also test the fallback: temporarily comment out the `server.headers` line, reload, repeat step 4, and expect `stopped: true` via worker restart with the RAM count preserved. Then restore the headers.

- [ ] **Step 7: Restore `src/main.tsx`** to the v1 version (`git checkout src/main.tsx`). It will render the new App in Task 11. Run `npx tsc --noEmit`. Errors in `src/app/*` that reference deleted modules are expected until Tasks 10–12, so only check that `src/engine/*` has no errors.

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "v2: Pyodide worker runs the world live with pacing, Stop and COI service worker"
```

---

### Task 9: Save format v2

**Files:**
- Rewrite: `src/engine/save.ts`
- Test: `tests/save.test.ts`

**Interfaces:**
- Consumes: `WorldState` (Task 8).
- Produces:
  ```ts
  export interface Settings { speed: number; follow: boolean }
  export interface Save { v: 2; world: WorldState | null; files: Record<string, string>; active: string; settings: Settings }
  export const STARTER: string;
  export function emptySave(): Save;
  export function loadSave(): Save;
  export function storeSave(save: Save): void;
  export function encodeSave(save: Save): string;   // "BW2." + base64(UTF-8 JSON)
  export function decodeSave(code: string): Save | null;
  ```

- [ ] **Step 1: Write the failing tests**

`tests/save.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { decodeSave, emptySave, encodeSave, STARTER } from "../src/engine/save";

describe("save v2", () => {
  it("starts with the welcome program", () => {
    const s = emptySave();
    expect(s.files["main.py"]).toBe(STARTER);
    expect(s.active).toBe("main.py");
    expect(s.world).toBeNull();
  });

  it("round-trips, including emoji in code", () => {
    const s = { ...emptySave(), files: { "main.py": "print('🏭 héllo')", "helpers.py": "" } };
    expect(decodeSave(encodeSave(s))).toEqual(s);
  });

  it("rejects junk, v1 codes and broken shapes", () => {
    expect(decodeSave("nope")).toBeNull();
    expect(decodeSave("BW1.e30=")).toBeNull();
    expect(decodeSave("BW2.!!!")).toBeNull();
    const bad = { ...emptySave(), active: "missing.py" };
    expect(decodeSave(encodeSave(bad as never))).toBeNull();
  });
});
```

- [ ] **Step 2: Run to check they fail**

Run: `npx vitest run`
Expected: FAIL (`STARTER` is not exported).

- [ ] **Step 3: Rewrite `src/engine/save.ts`**

```ts
import type { WorldState } from "./types";

export interface Settings { speed: number; follow: boolean }
export interface Save { v: 2; world: WorldState | null; files: Record<string, string>; active: string; settings: Settings }

const KEY = "byteworks.save.v2";

export const STARTER = `# Welcome to ByteWorks! Press Run (or Ctrl+Enter).
# Your drone harvests the RAM stick under it, moves East, then harvests again.
harvest()
move(East)
harvest()
`;

export const emptySave = (): Save => ({
  v: 2, world: null, files: { "main.py": STARTER }, active: "main.py", settings: { speed: 1, follow: true },
});

function isSave(x: unknown): x is Save {
  const s = x as Save;
  return !!s && s.v === 2
    && typeof s.files === "object" && s.files !== null
    && Object.values(s.files).every((v) => typeof v === "string") && "main.py" in s.files
    && typeof s.active === "string" && s.active in s.files
    && !!s.settings && typeof s.settings.speed === "number" && typeof s.settings.follow === "boolean"
    && (s.world === null || (typeof s.world === "object" && "inventory" in s.world && "floors" in s.world));
}

export function loadSave(): Save {
  try {
    const parsed = JSON.parse(localStorage.getItem(KEY) ?? "null");
    return isSave(parsed) ? parsed : emptySave();
  } catch {
    return emptySave();
  }
}

export function storeSave(save: Save): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(save));
  } catch {
    /* storage blocked or full: progress just won't persist */
  }
}

export function encodeSave(save: Save): string {
  const bytes = new TextEncoder().encode(JSON.stringify(save));
  let binary = "";
  bytes.forEach((b) => (binary += String.fromCharCode(b)));
  return "BW2." + btoa(binary);
}

export function decodeSave(code: string): Save | null {
  try {
    const trimmed = code.trim();
    if (!trimmed.startsWith("BW2.")) return null;
    const bytes = Uint8Array.from(atob(trimmed.slice(4)), (c) => c.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    return isSave(parsed) ? parsed : null;
  } catch {
    return null;
  }
}
```

- [ ] **Step 4: Run to check they pass**

Run: `npx vitest run`
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "v2: save format with world state, code windows and settings"
```

---

### Task 10: Floor screen, drone and inventory

**Files:**
- Rewrite: `src/floors.ts`, `src/app/FloorView.tsx`
- Create: `src/app/floorMath.ts`, `src/app/InventoryBar.tsx`, `tests/floor.test.ts`
- Test (Python): add `test_win_constant_matches` to `tests/test_game.py`

**Interfaces:**
- Consumes: `WorldState`, `Tile` (Task 8).
- Produces:
  ```ts
  // floors.ts
  export interface FloorInfo { id: string; label: string; name: string; icon: string; color: string; unlock: string | null }
  export const FLOORS: FloorInfo[];                  // bottom → top: RAM, CPU, SSD, BOARD, GPU, ASSEMBLY
  export const PART_ICON: Record<string, string>;
  export const PARTS_ORDER: string[];                // RAM, CPU, SSD, BOARD, GPU, COMPUTER
  export const WIN_COMPUTERS = 10;                   // must equal balance.WIN_COMPUTERS
  // floorMath.ts
  export interface TileLook { part: string | null; ready: boolean; progress: number; faulty: boolean; score: number | null }
  export function lookOf(tile: Tile, clock: number): TileLook;
  export function moveDuration(prev: DronePos | null, next: DronePos, animMs: number): number;
  export function svgRow(y: number, size: number): number;
  export interface DronePos { floor: string; x: number; y: number }
  // components
  export function FloorView(props: { floor: FloorInfo; world: WorldState; animMs: number; locked: boolean; lockedBy: string }): JSX.Element;
  export function InventoryBar(props: { world: WorldState | null }): JSX.Element;
  ```

- [ ] **Step 1: Write the failing tests**

`tests/floor.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { lookOf, moveDuration, svgRow } from "../src/app/floorMath";

describe("tile looks", () => {
  it("shows growth progress", () => {
    const look = lookOf(["CPU", 200, false, null, 100], 150);
    expect(look).toEqual({ part: "CPU", ready: false, progress: 0.5, faulty: false, score: null });
  });
  it("hides a faulty board until it's ready", () => {
    expect(lookOf(["BOARD", 200, true, null, 100], 150).faulty).toBe(false);
    expect(lookOf(["BOARD", 200, true, null, 100], 250).faulty).toBe(true);
  });
  it("shows GPU scores and handles empty tiles", () => {
    expect(lookOf(["GPU", 0, false, 7, 0], 5).score).toBe(7);
    expect(lookOf([null, 0, false, null, 0], 5)).toEqual({ part: null, ready: false, progress: 0, faulty: false, score: null });
  });
});

describe("drone movement", () => {
  const at = (x: number, y: number, floor = "RAM") => ({ floor, x, y });
  it("slides one step", () => expect(moveDuration(at(0, 0), at(1, 0), 200)).toBe(200));
  it("jumps when wrapping round an edge", () => expect(moveDuration(at(2, 0), at(0, 0), 200)).toBe(0));
  it("jumps when changing floor or on first draw", () => {
    expect(moveDuration(at(0, 0), at(0, 0, "CPU"), 200)).toBe(0);
    expect(moveDuration(null, at(0, 0), 200)).toBe(0);
  });
  it("puts North at the top", () => expect(svgRow(0, 3)).toBe(2));
});
```

Append to `tests/test_game.py`:
```python
class ConstantsTests(unittest.TestCase):
    def test_win_constant_matches(self):
        floors_ts = (Path(__file__).resolve().parent.parent / "src" / "floors.ts").read_text()
        self.assertIn(f"export const WIN_COMPUTERS = {B.WIN_COMPUTERS};", floors_ts)
```

- [ ] **Step 2: Run to check they fail**

Run: `npx vitest run tests/floor.test.ts` → FAIL (module not found). `npm run test:py` → FAIL (`WIN_COMPUTERS` not in floors.ts).

- [ ] **Step 3: Write `src/floors.ts`**

```ts
export interface FloorInfo { id: string; label: string; name: string; icon: string; color: string; unlock: string | null }

// Bottom to top. `unlock` is the upgrade that opens the floor (null = open from the start).
export const FLOORS: FloorInfo[] = [
  { id: "RAM", label: "G", name: "RAM Floor", icon: "🧠", color: "#4cc38a", unlock: null },
  { id: "CPU", label: "1", name: "CPU Floor", icon: "🔲", color: "#5aa9ff", unlock: "floor_cpu" },
  { id: "SSD", label: "2", name: "SSD Floor", icon: "💾", color: "#b18cff", unlock: "floor_ssd" },
  { id: "BOARD", label: "3", name: "Motherboard Floor", icon: "🟩", color: "#3fd0c9", unlock: "floor_board" },
  { id: "GPU", label: "4", name: "GPU Floor", icon: "🎮", color: "#ff7a59", unlock: "floor_gpu" },
  { id: "ASSEMBLY", label: "5", name: "Final Assembly", icon: "🖥️", color: "#ff5c8a", unlock: "floor_assembly" },
];

export const PART_ICON: Record<string, string> = { RAM: "🧠", CPU: "🔲", SSD: "💾", BOARD: "🟩", GPU: "🎮", COMPUTER: "🖥️" };
export const PARTS_ORDER = ["RAM", "CPU", "SSD", "BOARD", "GPU", "COMPUTER"];

// Keep equal to WIN_COMPUTERS in src/python/game/balance.py (a Python test checks this).
export const WIN_COMPUTERS = 10;
```

- [ ] **Step 4: Write `src/app/floorMath.ts`**

```ts
import type { Tile } from "../engine/types";

export interface TileLook { part: string | null; ready: boolean; progress: number; faulty: boolean; score: number | null }
export interface DronePos { floor: string; x: number; y: number }

export function lookOf(tile: Tile, clock: number): TileLook {
  const [part, readyAt, faulty, score, plantedAt] = tile;
  if (part === null) return { part: null, ready: false, progress: 0, faulty: false, score: null };
  const ready = clock >= readyAt;
  const progress = ready ? 1 : Math.min(1, Math.max(0, (clock - plantedAt) / Math.max(1, readyAt - plantedAt)));
  return { part, ready, progress, faulty: part === "BOARD" && ready && faulty, score: part === "GPU" ? score : null };
}

/** How long the drone should glide to its new spot: no glide across a wrapped edge or a floor change. */
export function moveDuration(prev: DronePos | null, next: DronePos, animMs: number): number {
  if (!prev || prev.floor !== next.floor) return 0;
  if (Math.abs(prev.x - next.x) > 1 || Math.abs(prev.y - next.y) > 1) return 0;
  return animMs;
}

/** SVG rows count down from the top, but North (+y) is up on screen. */
export function svgRow(y: number, size: number): number {
  return size - 1 - y;
}
```

- [ ] **Step 5: Write `src/app/FloorView.tsx`**

```tsx
import { useRef } from "preact/hooks";
import type { WorldState } from "../engine/types";
import { PART_ICON, WIN_COMPUTERS, type FloorInfo } from "../floors";
import { lookOf, moveDuration, svgRow, type DronePos } from "./floorMath";

const CELL = 100;

interface Props { floor: FloorInfo; world: WorldState; animMs: number; locked: boolean; lockedBy: string }

export function FloorView({ floor, world, animMs, locked, lockedBy }: Props) {
  const prev = useRef<DronePos | null>(null);
  const state = world.floors[floor.id];
  if (locked || !state) {
    return (
      <div class="floor-locked">
        <div class="floor-locked-icon">🔒</div>
        <div>{floor.name} is locked</div>
        <small>Buy “{lockedBy}” in the Upgrades tree.</small>
      </div>
    );
  }
  if (floor.id === "ASSEMBLY") return <AssemblyView world={world} />;

  const n = state.size;
  const pos = { floor: world.floor, x: world.x, y: world.y };
  const duration = moveDuration(prev.current, pos, animMs);
  prev.current = pos;

  return (
    <svg class="floor-svg" viewBox={`0 0 ${n * CELL} ${n * CELL}`} role="img" aria-label={`${floor.name}: ${n} by ${n} grid`}
      style={{ "--floor": floor.color }}>
      {state.grid.map((column, x) => column.map((tile, y) => {
        const look = lookOf(tile, world.clock);
        return (
          <g key={`${x}-${y}`} transform={`translate(${x * CELL} ${svgRow(y, n) * CELL})`}>
            <rect x="4" y="4" width="92" height="92" rx="10" class={`tile${look.ready ? " ready" : ""}${look.faulty ? " faulty" : ""}`} />
            {look.part && <text x="50" y="62" text-anchor="middle" class="tile-icon" opacity={look.ready ? 1 : 0.4}>{PART_ICON[look.part]}</text>}
            {look.part && !look.ready && <rect x="14" y="80" width={72 * look.progress} height="7" rx="3" class="grow-bar" />}
            {look.faulty && <text x="74" y="32" class="tile-flag">⚠️</text>}
            {look.score !== null && <text x="84" y="28" text-anchor="middle" class="tile-score">{look.score}</text>}
          </g>
        );
      }))}
      {world.floor === floor.id && (
        <g class="drone" style={{ transform: `translate(${world.x * CELL}px, ${svgRow(world.y, n) * CELL}px)`, transitionDuration: `${duration}ms` }}>
          <circle cx="50" cy="50" r="36" class="drone-ring" />
          <text x="50" y="64" text-anchor="middle" class="drone-icon">🤖</text>
        </g>
      )}
    </svg>
  );
}

function AssemblyView({ world }: { world: WorldState }) {
  const computers = world.inventory.COMPUTER ?? 0;
  return (
    <div class="assembly">
      <p class="assembly-drone">{world.floor === "ASSEMBLY" ? "🤖 The drone is at the assembly bench." : "The drone is on another floor."}</p>
      <h3>Order #{world.orders_done + 1}</h3>
      <ul class="order">
        {Object.entries(world.order ?? {}).map(([part, need]) => {
          const have = world.inventory[part] ?? 0;
          return <li key={part} class={have >= need ? "ok" : ""}>{PART_ICON[part]} {part}: {have} / {need}</li>;
        })}
      </ul>
      <p class="computers">🖥️ Computers built: <strong>{computers}</strong> / {WIN_COMPUTERS}</p>
      {computers >= WIN_COMPUTERS && <p class="win">🏆 ByteWorks is back in business! Keep going for fun.</p>}
    </div>
  );
}
```

- [ ] **Step 6: Write `src/app/InventoryBar.tsx`**

```tsx
import type { WorldState } from "../engine/types";
import { FLOORS, PARTS_ORDER, PART_ICON } from "../floors";

const UNLOCK_FOR_PART: Record<string, string | null> = {
  ...Object.fromEntries(FLOORS.map((f) => [f.id, f.unlock])), COMPUTER: "floor_assembly",
};

export function InventoryBar({ world }: { world: WorldState | null }) {
  if (!world) return <div class="inventory">Starting…</div>;
  const owned = new Set(world.unlocks);
  const shown = PARTS_ORDER.filter((p) => !UNLOCK_FOR_PART[p] || owned.has(UNLOCK_FOR_PART[p]!) || (world.inventory[p] ?? 0) > 0);
  return (
    <div class="inventory" aria-label="Parts you have">
      {shown.map((p) => (
        <span class="inv" key={p} title={p}>{PART_ICON[p]} <b>{(world.inventory[p] ?? 0).toLocaleString()}</b></span>
      ))}
    </div>
  );
}
```

- [ ] **Step 7: Run the tests to check they pass**

Run: `npx vitest run tests/floor.test.ts && npm run test:py`
Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add -A && git commit -m "v2: floor grid view with drone animation, assembly view and inventory bar"
```

---

### Task 11: Code panel and App wiring (first fully playable build)

**Files:**
- Create: `src/app/CodePanel.tsx`
- Rewrite: `src/app/App.tsx`, `src/app/styles.css` (per Step 4)
- Modify: `src/app/SaveDialog.tsx`, `src/engine/game.ts` (add public `reload`)
- Delete: `src/app/Lesson.tsx`, `src/app/Workbench.tsx`
- Keep: `src/app/Editor.tsx` (unchanged), `src/main.tsx` (renders `<App />`)

**Interfaces:**
- Consumes: `game` (Task 8), save API (Task 9), `FloorView`, `InventoryBar`, `FLOORS` (Task 10), `Editor` (v1: `{value, docKey, onChange, onRun}`).
- Produces:
  - `GameRunner.reload(state: WorldState | null): void` (terminate + start fresh, used by load/reset)
  - `CodePanel` props:
    ```ts
    export interface ConsoleLine { text: string; kind: "out" | "err" | "info" }
    interface CodePanelProps {
      files: Record<string, string>; active: string; windows: number; editKey: number;
      running: boolean; ready: boolean; speed: number; turbo: boolean; lines: ConsoleLine[];
      onEdit: (text: string) => void; onSelect: (name: string) => void;
      onAdd: (name: string) => void; onDelete: (name: string) => void;
      onRun: () => void; onStop: () => void; onSpeed: (speed: number) => void; onClear: () => void;
    }
    ```
  - `App` holds `panel: "none" | "upgrades" | "help" | "save"` and `helpId: string`. Task 12 plugs `UpgradePanel` and `HelpPanel` into those slots.

- [ ] **Step 1: Add `reload` to `GameRunner`** (in `src/engine/game.ts`, next to `restart`):

```ts
  /** Throw away the current world and start from `state` (a loaded save, or null for a new game). */
  reload(state: WorldState | null) {
    this.latest = state;
    this.restart();
  }
```

Note: `restart()` calls `this.start(this.latest)`, so setting `latest` first is what makes `reload` start from the given state.

- [ ] **Step 2: Write `src/app/CodePanel.tsx`**

```tsx
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
```

- [ ] **Step 3: Rewrite `src/app/App.tsx`**

```tsx
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
```

Note: `onBuy` and `helpId` are used by Task 12. Until then TypeScript may warn that they're unused. If `noUnusedLocals` is off (it is, in `tsconfig.json`), there's nothing to do.

- [ ] **Step 4: Update `SaveDialog.tsx` and `styles.css`**

`SaveDialog.tsx`: add a `running: boolean` prop. Disable "Load save" and "Reset all progress" while running, with the text "Stop your program first.". Change the placeholder to `Paste a code starting with BW2.` and the intro text to: "Progress saves automatically in this browser. To carry on from another computer, copy your save code and load it there." Everything else stays the same (it already uses `encodeSave`/`decodeSave`).

`styles.css`: keep the v1 tokens, `body`, `.btn*`, `.elevator/.lift/.floor-list/.floor-btn`, `.modal*`, `.panel`, `.spacer`, `.kbd-hint` and `.foot` rules. Delete the rules for `.lesson*`, `.briefing`, `.bonus`, `.tryit*` (Task 12 re-adds them), `.workbench*`, `.day-tab*`, `.machine*`, `.bin-*`, `.part-label`, `.result*`, `.hints`, `.hint`, `.floor-sign`, `.screen-text`, `.progress*`, `.locked-text`, `.darkness`, `.slide-*`. Then append:
```css
.topbar { display: flex; align-items: center; gap: 12px; padding: 12px 0; flex-wrap: wrap; }
.inventory { display: flex; gap: 8px; flex-wrap: wrap; }
.inv { background: var(--panel); border: 1px solid var(--line); border-radius: 99px; padding: 2px 10px; font-size: 0.95rem; }
.badge { margin-left: 6px; background: var(--accent); color: var(--accent-ink); border-radius: 99px; padding: 0 7px; font-size: 0.8rem; }
.game { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 16px; align-items: start; }
.building { display: flex; gap: 10px; }
.floor-frame { flex: 1; min-width: 0; background: var(--panel); border: 2px solid var(--floor); border-radius: var(--radius); padding: 10px; }
.floor-head { display: flex; justify-content: space-between; align-items: center; font-weight: 700; margin-bottom: 8px; }
.follow { font-weight: 400; font-size: 0.9rem; color: var(--muted); display: flex; gap: 6px; align-items: center; }
.floor-btn.drone { outline: 2px dashed var(--accent); outline-offset: 1px; }
.floor-svg { display: block; width: 100%; height: auto; max-height: 70vh; }
.tile { fill: var(--panel-2); stroke: var(--line); stroke-width: 2; }
.tile.ready { stroke: var(--floor); }
.tile.faulty { fill: #4a1f24; stroke: var(--bad); }
.tile-icon { font-size: 40px; }
.tile-flag { font-size: 24px; }
.tile-score { fill: #fff; font: 700 22px var(--mono); }
.grow-bar { fill: var(--floor); }
.drone { transition-property: transform; transition-timing-function: linear; }
.drone-ring { fill: #0008; stroke: var(--accent); stroke-width: 4; }
.drone-icon { font-size: 40px; }
.floor-locked { min-height: 280px; display: grid; place-content: center; text-align: center; gap: 6px; color: var(--muted); }
.floor-locked-icon { font-size: 3rem; }
.assembly { padding: 8px 12px; }
.order { list-style: none; padding: 0; display: grid; gap: 6px; }
.order li { background: var(--panel-2); border-radius: 8px; padding: 6px 10px; }
.order li.ok { outline: 2px solid var(--ok); }
.win { color: var(--accent); font-weight: 700; font-size: 1.1rem; }
.code-panel { display: flex; flex-direction: column; gap: 10px; }
.tabs { display: flex; gap: 6px; flex-wrap: wrap; }
.tab { display: flex; align-items: center; background: var(--panel-2); border: 1px solid var(--line); border-radius: 8px 8px 0 0; }
.tab.active { border-color: var(--accent); }
.tab-name, .tab-x, .tab.add { background: none; border: 0; color: var(--text); font: inherit; padding: 6px 10px; cursor: pointer; }
.tab-x.danger { color: var(--bad); }
.add-form { display: flex; align-items: center; gap: 4px; padding: 4px 6px; }
.add-form input { width: 110px; font: 0.9rem var(--mono); background: #0f1218; color: var(--text); border: 1px solid var(--line); border-radius: 6px; padding: 3px 6px; }
.hint-line { color: #ffb4a8; font-size: 0.85rem; }
.controls { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.speed { display: flex; gap: 4px; }
.btn.on { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.console { background: #0a0d0a; border: 1px solid var(--line); border-radius: 8px; }
.console-head { display: flex; justify-content: space-between; align-items: center; padding: 4px 10px; border-bottom: 1px solid var(--line); color: var(--muted); font-size: 0.85rem; }
.console-body { height: 180px; overflow-y: auto; padding: 8px 10px; font: 0.88rem var(--mono); white-space: pre-wrap; }
.line.out { color: #b9f5c4; }
.line.err { color: #ffb4a8; }
.line.info { color: var(--muted); }
.toast { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%); padding: 10px 16px; border-radius: 8px; background: var(--panel-2); }
.toast.err { border: 1px solid var(--bad); }
@media (max-width: 900px) { .game { grid-template-columns: 1fr; } }
@media (max-width: 560px) {
  .building { flex-direction: column-reverse; }
  .elevator { flex-direction: row; justify-content: center; }
  .floor-list { flex-direction: row-reverse; }
}
```

- [ ] **Step 5: Type-check, test and build**

```bash
git rm -q src/app/Lesson.tsx src/app/Workbench.tsx
npx tsc --noEmit && npm test && npm run build
```
Expected: no type errors, all tests pass, build succeeds.

- [ ] **Step 6: Play it in Chrome**

`npx vite --port 5317` (in the background), then in a new Chrome tab at `http://localhost:5317/`:
1. Fresh load: the welcome program is in `main.py` and the RAM floor is a 3×3 grid with the drone. (The Help panel slot opens in Task 12, so for now `panel` is `"help"` with nothing rendered, which is fine.)
2. Press **Run**. The drone harvests, glides East and harvests again. The inventory shows 🧠 2. The console shows `▶ Running main.py` then `✓ Program finished`.
3. Type `while True:` code. Run shows the red "you haven't unlocked while loops yet… Loops" error and nothing moves.
4. Reload the page: RAM count and code are kept.
5. Seed a richer save through the JS tool (`localStorage` edit with `unlocks: ["loops"]` is not enough, because the world lives in the worker, so instead run the starter three times and use `await game.buy("loops")` through `window`: temporarily add `(window as any).game = game` in `main.tsx` and remove it before committing). Then run `while True:\n    harvest()\n    move(North)` at x4, press **Stop** after 2 s: it stops within one action and the console shows `■ Stopped`.
6. Narrow the window to 390 px wide: floor and code stack vertically, and there's no sideways scroll.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "v2: playable game screen with code windows, run/stop, speed and console"
```

---

### Task 12: Upgrade tree panel, help pages and "Try it" boxes

**Files:**
- Create: `src/app/UpgradePanel.tsx`, `src/app/HelpPanel.tsx`, `src/app/tryit.ts`
- Create: `src/help/*.md` (21 pages, listed below)
- Create: `tests/test_help.py`
- Modify: `src/app/App.tsx` (render the two panels), `src/app/styles.css` (panel + help styles)
- Delete: `src/help/_v1/` (at the end of the task)

**Interfaces:**
- Consumes: `game.snippet` (Task 8), `UnlockInfo`, `BuyResult`, `WorldState` (Task 8), App's `panel/helpId/onBuy` (Task 11), `gating.check`, `sandbox.run_snippet`, `unlocks.BY_ID` (Python).
- Produces:
  ```ts
  export function UpgradePanel(props: { tree: UnlockInfo[]; world: WorldState; running: boolean;
    onBuy: (id: string) => Promise<BuyResult>; onHelp: (helpId: string) => void; onClose: () => void }): JSX.Element;
  export function HelpPanel(props: { helpId: string; tree: UnlockInfo[]; owned: Set<string>; running: boolean;
    onPick: (helpId: string) => void; onClose: () => void }): JSX.Element;
  export function attachTryIt(root: HTMLElement, canRun: () => boolean): void;
  ```
- Help page conventions (the tests enforce these):
  - The file name is the unlock's `help` id (`loops.md`, `floor_cpu.md`…) plus `start.md`. The first line is `# Title`.
  - ` ```python ` blocks are **runnable plain-Python examples**. They must run without errors in `run_snippet` and must not call drone functions.
  - ` ```py ` blocks are **drone examples** (shown, not run). They must pass `gating.check` using only the unlocks owned at that point: the page's unlock plus its prerequisites (`start.md` = nothing unlocked).

- [ ] **Step 1: Write the failing help test**

`tests/test_help.py`:
```python
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))

from game import unlocks as U  # noqa: E402
from game.gating import check  # noqa: E402
from game.sandbox import run_snippet  # noqa: E402

HELP = ROOT / "src" / "help"
BLOCK = re.compile(r"```(python|py)\n(.*?)```", re.S)


def owned_at(page):
    if page == "start":
        return set()
    wanted, todo = set(), [page]
    while todo:
        uid = todo.pop()
        if uid not in wanted:
            wanted.add(uid)
            todo.extend(U.BY_ID[uid].requires)
    return wanted


class HelpPageTests(unittest.TestCase):
    def test_every_help_id_has_a_page(self):
        ids = {u.help for u in U.UNLOCKS if u.help} | {"start"}
        missing = [i for i in sorted(ids) if not (HELP / f"{i}.md").exists()]
        self.assertEqual(missing, [])

    def test_examples(self):
        for path in sorted(HELP.glob("*.md")):
            text = path.read_text()
            self.assertTrue(text.startswith("# "), f"{path.name} must start with '# Title'")
            unlocked = owned_at(path.stem)
            for kind, code in BLOCK.findall(text):
                if kind == "python":
                    result = run_snippet(code)
                    self.assertIsNone(result["error"], f"{path.name} example failed:\n{code}\n{result['error']}")
                else:
                    problems = check(code, unlocked, "main.py", set())
                    self.assertEqual(problems, [], f"{path.name} drone example uses locked things:\n{code}")


if __name__ == "__main__":
    unittest.main()
```

Run: `npm run test:py` → FAIL (missing pages).

- [ ] **Step 2: Write the help pages**

Tone: friendly, for complete beginners, short sections, UK spelling. Every page ends with a `## Try this` challenge (one or two sentences, no code). Where a v1 lesson is named as the source, copy its explanations and plain-Python examples, then **delete** every "Your task" section and anything about the old factory story. Drone examples use ` ```py `.

`src/help/start.md` (write in full):
````markdown
# Welcome to ByteWorks

The old ByteWorks computer factory has been abandoned for years. Its machines are gone, but one little **drone** 🤖 still works, and it does exactly what your **Python code** tells it to.

Your job: write code that makes the drone gather computer parts, spend those parts on **upgrades**, and slowly bring every floor of the factory back to life.

## Your first commands

| Command | What the drone does |
|---|---|
| `harvest()` | collects the part it's hovering over |
| `move(North)` | moves one square (also `East`, `South`, `West`) |
| `print("hi")` | writes a message in the Console |

Python runs your code **from top to bottom, one line at a time**:

```py
harvest()
move(East)
harvest()
move(North)
harvest()
```

Press **▶ Run** (or **Ctrl + Enter**) and watch the drone. When it reaches an edge of the floor, it wraps round to the other side.

## Comments

A line starting with `#` is a **comment**. Python skips it, so it's a note for humans:

```python
# This line is ignored
print("This line runs")  # comments can go at the end of a line too
```

## Things take time

Every action takes a moment of game time. A RAM stick needs a little while to **regrow** after you harvest it. Harvest too soon and you get nothing.

## Upgrades

Parts are money. Open **⬆️ Upgrades** to spend them. Your first goal is **Loops (5 RAM)**. With loops, the drone can work forever without you pressing Run again. Each upgrade teaches a new bit of Python, and you'll find its page here in Help.

## Try this

Write a program that harvests all 9 RAM sticks on the floor, then buy **Loops**.
````

For each page below, write it following the same conventions:

| File | Title | Source (copy explanations + `python` examples from) | Must cover | Drone example(s) (` ```py `) |
|---|---|---|---|---|
| `loops.md` | Loops | `_v1/day10.md` sections "Loops", "The while loop", "break and continue" | `while True:`, `while` with a condition, infinite loops are normal here and **Stop** ends them, indentation, `break`, `continue`, `wait(ticks)` | `while True:` harvest + `move(North)`; a sweep that also moves East every time round |
| `variables.md` | Variables & Operators | `_v1/day02.md` ("Variables", "Naming rules", "The four basic types"), `_v1/day03.md` (all four operator families) | assignment, naming, int/float/str/bool, arithmetic, `+=`, comparisons, `and/or/not`, `num_items(Part.RAM)`, `int()/float()/abs()/min()/max()/round()` | counting harvests with a variable; `while num_items(Part.RAM) < 50:` |
| `conditionals.md` | Conditionals | `_v1/day09.md` | `if/elif/else`, order matters, one-line `x if c else y`, `can_harvest()`, `get_part()` returns a part name or `None` | `if can_harvest(): harvest()` inside a `while True` loop |
| `floor_cpu.md` | The CPU Floor | (new) | `goto_floor(Floor.CPU)` and back, the lift takes time, `get_floor()`, `place(Part.CPU)` on empty tiles, baking, **harvesting early destroys the chip**, the progress bar | a loop that visits CPU tiles: harvest if ready, place if empty (`get_part() == None`) |
| `for_loops.md` | For Loops & range | `_v1/day10.md` ("The for loop", "range()", "Extras: nested loops…") | `for x in …`, `range(n)`, `range(a, b, step)`, nested loops, `for … else`, `pass` | sweeping a 3×3 floor with nested `for` loops |
| `positions.md` | Positions & Tuples | `_v1/day06.md` | tuples, immutability, unpacking, `get_pos()` → `(x, y)`, `get_world_size()` | `x, y = get_pos()`, and a sweep using `get_world_size()` so it works on any grid size |
| `functions.md` | Functions | `_v1/day11.md` | `def`, calling, parameters, `return`, defaults, keyword arguments, `*args`, functions calling functions, `global` (briefly) | `def tend():` that sweeps a floor, called for two floors |
| `floor_ssd.md` | The SSD Floor | (new) | `place(Part.SSD)` costs 3 RAM + 1 CPU (look in Upgrades/costs), yields 2, planning with `num_items`, visiting several floors in one program | a function that only places an SSD if `num_items(Part.RAM) >= 3 and num_items(Part.CPU) >= 1` |
| `lists.md` | Lists | `_v1/day05.md` | lists, indexing, slicing, mutability, methods table, `in`, `len`, `+` | a list of floors to visit in a loop |
| `strings.md` | Strings & f-strings | `_v1/day04.md` | strings, indexing/slicing, methods table, f-strings | `print(f"RAM: {num_items(Part.RAM)}")` status report |
| `floor_board.md` | The Motherboard Floor | (new) | `place(Part.BOARD)` costs 2 SSD, ~1 in 5 boards come out **faulty** (red ⚠️ once ready), `is_faulty()`, harvesting a faulty board raises `FaultyBoardError` and stops your program, fix it by placing a new board over it, **merging**: a full k×k square of good ready boards pays k³ when harvested | `if is_faulty(): place(Part.BOARD) elif can_harvest(): harvest()`; tip: wait until the whole floor is ready, then harvest once |
| `sets.md` | Sets | `_v1/day07.md` | uniqueness, `set()`, add/remove/discard, union/intersection/difference, membership | remembering positions of faulty boards in a set of `get_pos()` tuples |
| `dicts.md` | Dictionaries | `_v1/day08.md` | key/value, add/change, `.get()`, `.pop()`, `keys/values/items`, looping over `items()` | a dict of floor → part to place, used in a loop |
| `comprehensions.md` | Comprehensions & lambda | `_v1/day13.md` | list/dict/set comprehensions with `if`, flattening, lambda | building a list of all `(x, y)` positions with a comprehension |
| `hof.md` | Higher-order Functions | `_v1/day14.md` | functions as values, `map`, `filter`, `sorted(key=)`, `min/max(key=)`, closures, decorators | `sorted(floors, key=lambda f: num_items(f))` to visit the scarcest part first |
| `floor_gpu.md` | The GPU Floor | (new) | `place(Part.GPU)` costs 1 BOARD + 2 CPU, every chip has a score 0–9 (shown on the tile), `measure()`, `swap(direction)` (no wrap at edges), the **sorted bonus**: if every row increases going East and every column increases going North when you harvest a ready chip, the whole floor pays n² per chip; otherwise 1; explain bubble sort in words first | one bubble-sort pass along a row: for each column, `here = measure()`, `move(East)`, `right = measure()`, `move(West)`, `if here > right: swap(East)`, then `move(East)` (a `for` loop over `range(get_world_size() - 1)`) |
| `modules.md` | Modules | `_v1/day12.md` ("Modules", "Ways to import", "The standard library" table, but only `math` and `random` are allowed here) | code windows are files, **+ New window**, `import helpers` then `helpers.tend()`, `from helpers import tend`, `import math`, `import random`, only `math`/`random`/your windows can be imported | `main.py` importing `helpers` (show both files as two ` ```py ` blocks; the helpers block defines a function) |
| `exceptions.md` | Exceptions | `_v1/day15.md` (error types, how to debug) and `_v1/day17.md` (try/except/else/finally/raise) | reading errors, common error types, `try/except`, named exceptions, `else`, `finally`, `raise`; why a bare `except:` isn't allowed (it would swallow Stop) | `try: harvest() except FaultyBoardError: place(Part.BOARD)` |
| `floor_assembly.md` | Final Assembly | (new) | `goto_floor(Floor.ASSEMBLY)`, `get_order()` gives a dict like `{"RAM": 20, "GPU": 4}`, `assemble()` uses the parts and builds 🖥️ 1 computer, returns False if you're short, orders grow, the goal is 10 computers | loop over `get_order().items()` to find what's missing, then `while assemble(): pass` |
| `classes.md` | Classes | `_v1/day21.md` | class, `__init__`, `self`, methods, `__str__`, inheritance, `super()` | an optional `OrderPlanner` class with a `missing()` method. Classes are optional in ByteWorks: say so |

Notes:
- The ` ```python ` examples in `modules.md` may import `math` and `random` only.
- In `exceptions.md`, runnable examples that demonstrate an error must catch it (`try/except`), so `run_snippet` reports no error.
- Keep each page's drone examples within its unlocks. `test_help.py` checks this. For example, `loops.md` examples can't use variables yet.

- [ ] **Step 3: Run the help test**

Run: `npm run test:py`
Expected: pass. For any failure the message names the page and the example, so fix the example rather than the test.

- [ ] **Step 4: Write `src/app/tryit.ts`** (moved from v1 `Lesson.tsx`, now using `game.snippet`):

```ts
import { game } from "../engine/game";

/** Turn every ```python block inside `root` into an editable box with a Run button. */
export function attachTryIt(root: HTMLElement, canRun: () => boolean) {
  root.querySelectorAll("pre > code.language-python").forEach((code) => {
    const pre = code.parentElement!;
    if (pre.parentElement?.classList.contains("tryit")) return;
    const box = document.createElement("div");
    box.className = "tryit";
    pre.replaceWith(box);
    box.appendChild(pre);
    code.setAttribute("contenteditable", "plaintext-only");
    code.setAttribute("spellcheck", "false");
    const bar = document.createElement("div");
    bar.className = "tryit-bar";
    const btn = document.createElement("button");
    btn.className = "btn small";
    btn.textContent = "▶ Try it";
    const out = document.createElement("pre");
    out.className = "tryit-out";
    out.hidden = true;
    btn.onclick = async () => {
      out.hidden = false;
      out.classList.remove("err");
      if (!canRun()) {
        out.textContent = "Stop your drone program first. Python can only do one thing at a time.";
        return;
      }
      btn.disabled = true;
      out.textContent = "Running…";
      try {
        const r = await game.snippet(code.textContent ?? "");
        out.textContent = (r.stdout || "") + (r.error ? (r.stdout ? "\n" : "") + r.error : "") || "(no output)";
        out.classList.toggle("err", !!r.error);
      } catch (e) {
        out.textContent = String(e);
        out.classList.add("err");
      } finally {
        btn.disabled = false;
      }
    };
    bar.append(btn);
    box.append(bar, out);
  });
}
```

- [ ] **Step 5: Write `src/app/HelpPanel.tsx`**

```tsx
import { useEffect, useMemo, useRef } from "preact/hooks";
import { marked } from "marked";
import type { UnlockInfo } from "../engine/types";
import { attachTryIt } from "./tryit";

const files = import.meta.glob("../help/*.md", { query: "?raw", import: "default", eager: true }) as Record<string, string>;
const PAGES: Record<string, string> = Object.fromEntries(
  Object.entries(files).map(([path, text]) => [path.split("/").pop()!.replace(/\.md$/, ""), text]),
);
const titleOf = (id: string) => (PAGES[id] ?? "# ?").split("\n")[0].replace(/^# /, "");

interface Props {
  helpId: string; tree: UnlockInfo[]; owned: Set<string>; running: boolean;
  onPick: (helpId: string) => void; onClose: () => void;
}

export function HelpPanel({ helpId, tree, owned, running, onPick, onClose }: Props) {
  const body = useRef<HTMLDivElement>(null);
  const runningRef = useRef(running);
  runningRef.current = running;
  const topics = ["start", ...tree.filter((u) => u.help && owned.has(u.id)).map((u) => u.help!)];
  const html = useMemo(() => marked.parse(PAGES[helpId] ?? PAGES.start, { async: false }) as string, [helpId]);

  useEffect(() => {
    if (!body.current) return;
    attachTryIt(body.current, () => !runningRef.current);
    body.current.scrollTop = 0;
  }, [html]);

  return (
    <aside class="drawer panel" role="dialog" aria-label="Help">
      <div class="drawer-head">
        <h2>📖 Help</h2>
        <button class="btn small" onClick={onClose}>Close</button>
      </div>
      <nav class="help-topics">
        {topics.map((id) => (
          <button key={id} class={`chip ${id === helpId ? "on" : ""}`} onClick={() => onPick(id)}>{titleOf(id)}</button>
        ))}
      </nav>
      <div class="help-body" ref={body} dangerouslySetInnerHTML={{ __html: html }} />
    </aside>
  );
}
```

- [ ] **Step 6: Write `src/app/UpgradePanel.tsx`**

```tsx
import { useState } from "preact/hooks";
import type { BuyResult, UnlockInfo, WorldState } from "../engine/types";
import { PART_ICON } from "../floors";

interface Props {
  tree: UnlockInfo[]; world: WorldState; running: boolean;
  onBuy: (id: string) => Promise<BuyResult>; onHelp: (helpId: string) => void; onClose: () => void;
}

export function UpgradePanel({ tree, world, running, onBuy, onHelp, onClose }: Props) {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const owned = new Set(world.unlocks);
  const canAfford = (u: UnlockInfo) => Object.entries(u.cost).every(([p, n]) => (world.inventory[p] ?? 0) >= n);
  const ready = tree.filter((u) => !owned.has(u.id) && u.requires.every((r) => owned.has(r)));
  const readyIds = new Set(ready.map((u) => u.id));
  // One step ahead only: items whose missing requirements are all buyable right now
  const next = tree.filter((u) => !owned.has(u.id) && !readyIds.has(u.id)
    && u.requires.every((r) => owned.has(r) || readyIds.has(r)));
  const done = tree.filter((u) => owned.has(u.id));
  const titleOf = (id: string) => tree.find((u) => u.id === id)?.title ?? id;

  const buy = async (u: UnlockInfo) => {
    setBusy(true);
    try {
      setMessage((await onBuy(u.id)).message);
    } finally {
      setBusy(false);
    }
  };

  const card = (u: UnlockInfo, state: "ready" | "next" | "done") => (
    <li key={u.id} class={`upgrade ${state} kind-${u.kind}`}>
      <div class="upgrade-title">{u.title}</div>
      <div class="upgrade-summary">{u.summary}</div>
      <div class="upgrade-cost">
        {Object.entries(u.cost).map(([p, n]) => (
          <span key={p} class={`cost ${(world.inventory[p] ?? 0) >= n ? "ok" : ""}`}>{PART_ICON[p]} {n}</span>
        ))}
      </div>
      {state === "ready" && (
        <button class="btn small primary" disabled={running || busy || !canAfford(u)} onClick={() => buy(u)}>
          {running ? "Stop program to buy" : canAfford(u) ? "Buy" : "Not enough parts"}
        </button>
      )}
      {state === "next" && <div class="upgrade-needs">Needs {u.requires.filter((r) => !owned.has(r)).map(titleOf).join(", ")}</div>}
      {state === "done" && u.help && <button class="btn small ghost" onClick={() => onHelp(u.help!)}>📖 Help</button>}
    </li>
  );

  return (
    <aside class="drawer panel" role="dialog" aria-label="Upgrades">
      <div class="drawer-head">
        <h2>⬆️ Upgrades</h2>
        <button class="btn small" onClick={onClose}>Close</button>
      </div>
      {message && <p class="upgrade-msg" role="status">{message}</p>}
      <h3>Available</h3>
      <ul class="upgrade-list">{ready.length ? ready.map((u) => card(u, "ready")) : <li class="empty">Nothing right now: keep harvesting!</li>}</ul>
      {next.length > 0 && <><h3>Coming up</h3><ul class="upgrade-list">{next.map((u) => card(u, "next"))}</ul></>}
      {done.length > 0 && <details><summary>Owned ({done.length})</summary><ul class="upgrade-list">{done.map((u) => card(u, "done"))}</ul></details>}
    </aside>
  );
}
```

- [ ] **Step 7: Plug the panels into `App.tsx`**

Replace the comment `{/* Task 12 adds: ... */}` with:
```tsx
      {panel === "upgrades" && world && (
        <UpgradePanel tree={tree} world={world} running={running} onBuy={onBuy} onClose={() => setPanel("none")}
          onHelp={(id) => { setHelpId(id); setPanel("help"); }} />
      )}
      {panel === "help" && (
        <HelpPanel helpId={helpId} tree={tree} owned={owned} running={running}
          onPick={setHelpId} onClose={() => setPanel("none")} />
      )}
```
and add the imports `import { UpgradePanel } from "./UpgradePanel";` and `import { HelpPanel } from "./HelpPanel";`.

- [ ] **Step 8: Styles** (append to `styles.css`):
```css
.drawer { position: fixed; top: 0; right: 0; bottom: 0; width: min(560px, 100%); overflow-y: auto; z-index: 20; border-radius: 0; box-shadow: -8px 0 30px #0008; }
.drawer-head { display: flex; justify-content: space-between; align-items: center; }
.drawer-head h2 { margin: 0; }
.help-topics { display: flex; flex-wrap: wrap; gap: 6px; margin: 12px 0; }
.chip { font: inherit; font-size: 0.85rem; background: var(--panel-2); color: var(--text); border: 1px solid var(--line); border-radius: 99px; padding: 3px 10px; cursor: pointer; }
.chip.on { background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }
.help-body h1 { font-size: 1.5rem; }
.help-body h2 { font-size: 1.2rem; margin-top: 24px; }
.help-body :not(pre) > code { background: var(--panel-2); padding: 1px 6px; border-radius: 5px; color: #ffd98a; }
.help-body pre { background: #0f1218; border: 1px solid var(--line); border-radius: 8px; padding: 12px; overflow-x: auto; }
.help-body code.language-py { color: #9fd3ff; }
.help-body table { border-collapse: collapse; width: 100%; display: block; overflow-x: auto; }
.help-body th, .help-body td { border: 1px solid var(--line); padding: 6px 10px; text-align: left; }
.tryit code[contenteditable] { display: block; outline: none; white-space: pre; }
.tryit-bar { display: flex; justify-content: flex-end; margin-top: 6px; }
.tryit-out { background: #0a0d0a !important; color: #b9f5c4; white-space: pre-wrap; }
.tryit-out.err { color: #ffb4a8; }
.upgrade-list { list-style: none; padding: 0; display: grid; gap: 8px; }
.upgrade { background: var(--panel-2); border: 1px solid var(--line); border-radius: 10px; padding: 10px 12px; display: grid; gap: 6px; }
.upgrade.next { opacity: 0.6; }
.upgrade.kind-floor { border-color: var(--accent); }
.upgrade-title { font-weight: 700; }
.upgrade-summary, .upgrade-needs { color: var(--muted); font-size: 0.9rem; }
.upgrade-cost { display: flex; gap: 6px; }
.cost { font: 0.85rem var(--mono); background: #0f1218; border-radius: 6px; padding: 2px 6px; color: #ffb4a8; }
.cost.ok { color: #b9f5c4; }
.upgrade-msg { color: var(--accent); }
.empty { color: var(--muted); }
```

- [ ] **Step 9: Delete the v1 source lessons, then test and build**

```bash
git rm -rq src/help/_v1
npx tsc --noEmit && npm test && npm run build
```
Expected: all green.

- [ ] **Step 10: Check in Chrome**

With `npx vite --port 5317` running: a fresh load opens Help on "Welcome to ByteWorks". A `python` block's **▶ Try it** prints output. Harvest 5 RAM and open Upgrades: **Loops** shows "Buy". Buying it opens the Loops help page, and a `while True` program now runs. While a program runs, Buy is disabled with "Stop program to buy", and Try it says to stop first.

- [ ] **Step 11: Commit**

```bash
git add -A && git commit -m "v2: upgrade tree panel, 21 help pages with tested examples, Try it boxes"
```

---

### Task 13: README, deploy workflow and full verification

**Files:**
- Rewrite: `README.md`
- Modify: `.github/workflows/deploy.yml`
- Update the project notes (outside the repo, not committed)

**Interfaces:**
- Consumes: everything.
- Produces: a deployable site and docs.

- [ ] **Step 1: Update the deploy workflow**

In `.github/workflows/deploy.yml`, replace the three steps `pip install numpy pandas beautifulsoup4`, `npx vitest run` and `python tests/run_levels.py` with:
```yaml
      - run: npx vitest run
      - run: python -m unittest discover -s tests -p "test_*.py"
```
Keep `python-version: "3.14"`, `npm ci`, `npm run build`, the Pages upload and the deploy job unchanged.

- [ ] **Step 2: Rewrite `README.md`**

Sections, in this order:
1. `# 🏭 ByteWorks` plus a one-paragraph pitch: a *The Farmer Was Replaced*-style game where you learn Python by programming a drone to rebuild a computer factory. Free, in the browser.
2. **How to play**: write code, Run/Stop, harvest parts, buy upgrades that unlock Python features and floors. Include a table of floors with each floor's puzzle (from the spec's floors table).
3. **What you learn**: a list of the unlock → Python topic pairs (the spec's upgrade-tree list).
4. **How it works**: Pyodide worker holds the world and runs your code, pacing with `Atomics.wait`, Stop via the interrupt buffer, `coi-serviceworker` for GitHub Pages, AST gating, and progress saved in the browser with a save code.
5. **Put it online (free, runs 24/7, your computer can be off)**: copy the v1 README's three steps unchanged.
6. **Run it locally**: `npm install`, `npm run dev`.
7. **Tests**: `npm test` (vitest + Python unit tests + help-page examples + the reference-bot playthrough).
8. **Project layout**: the File Structure tree from this plan.
9. **Tuning the game**: all numbers live in `src/python/game/balance.py` and the upgrade costs in `unlocks.py`, and `python3 -m unittest tests.test_progress -v` prints how long the reference bots take.

- [ ] **Step 3: Full test + build**

Run: `npm test && npm run build`
Expected: all tests pass, and the build succeeds with `dist/coi-serviceworker.min.js` present (`ls dist`).

- [ ] **Step 4: End-to-end check of the production build in Chrome**

`npx vite preview --port 5318` (background). In a new Chrome tab at `http://localhost:5318/`:
1. After the first load (the service worker may reload the page once), `crossOriginIsolated` is `true` (JavaScript tool).
2. Fresh game: Help shows Welcome. Run the starter and see RAM 2.
3. Farm, buy Loops, and run a `while True` sweep at x16. Stop works within one action.
4. Put `print(nope)` in a program: the console shows `Line 1: NameError…` in red.
5. Using the page's `game` object is not available in production, so progress through the tree by playing: farm with a loop, buy Variables and Conditionals, then the CPU Floor. Check the lift ▲/▼ and arrow keys, that follow-drone switches floors when the program calls `goto_floor(Floor.CPU)`, and that placing and baking CPUs shows progress bars.
6. Save → copy the code → Reset all progress → Load save → the progress is back.
7. At 390 px width, the layout stacks with no horizontal scroll.

Stop the preview and dev servers and close the tab afterwards.

- [ ] **Step 5: Update the project memory**

Rewrite the project notes so they describe v2: a TFWR-style automation game, core Python only, and the key paths (`src/python/game/`, `tests/test_progress.py`, `balance.py`). Keep the privacy note (only touch `~/projects/byteworks`). Update its line in `MEMORY.md` to match.

- [ ] **Step 6: Commit**

```bash
git add -A && git commit -m "v2: README and CI for the automation game"
```
