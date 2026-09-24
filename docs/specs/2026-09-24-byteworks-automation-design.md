# ByteWorks v2: a programming automation game (design)

Status: approved in chat on 2026-09-24. This replaces the v1 tutorial design (`2026-09-24-byteworks-design.md`).

## Goal

A free browser game in the style of *The Farmer Was Replaced*. It teaches complete beginners **core
Python** (30 Days of Python, days 1–17 and 21) through play, not lessons:

- You write Python that controls a **drone** moving around a grid on a factory floor.
- Code runs **live**: each action takes game time and you watch the drone do it. `while True:` loops
  run until you press Stop.
- Harvested computer parts are **currency**. You spend them in an **upgrade tree** that unlocks Python
  features, drone speed, bigger grids and new floors.
- Each floor builds a different computer part with its own puzzle, and the later puzzles force better code.

Out of scope, by the user's decision: Flask, MongoDB, pandas/NumPy, web scraping, APIs, venv/pip,
regex, file handling. There are no accounts or servers.

Constraints (unchanged from v1): static site on GitHub Pages, free, around 30 or more players at once, progress saved in the
browser with an export/import save code, a floor lift with ▲/▼ buttons and arrow keys. Only
`~/projects/byteworks` may be touched.

## Player experience

1. First load: the RAM floor is a 3×3 grid of RAM sticks. The only code window holds:
   ```python
   # Welcome to ByteWorks! Press Run.
   harvest()
   move(East)
   harvest()
   ```
   The drone harvests, moves and harvests again, and the inventory shows `RAM 2`.
2. The upgrade tree shows the first unlocks (e.g. **Loops: 5 RAM**). Buying one opens its **help page**
   (short beginner explanation plus examples, reusing v1 lesson text), and the feature can now be used.
3. Code that uses a locked feature doesn't run. It shows e.g. *"Line 3: you haven't unlocked `while` loops
   yet. Find them in the Upgrades tree."*
4. New floors open through upgrades. The drone takes the lift between floors with `goto_floor(Floor.CPU)`.
   The ▲/▼ buttons only move the **camera**, and a "follow drone" toggle keeps the camera on the drone.
5. The end goal is to assemble a set number of complete computers at Final Assembly and restore the
   factory. After that the game carries on as a sandbox.

## World model (Python, runs in the worker)

- **Game clock**: counts in ticks. It only moves forward when the drone acts. Every action has a tick cost, and
  `wait(ticks)` exists. While no program is running, time is frozen. This keeps everything deterministic
  and testable.
- **Pacing**: real delay per action = `ticks × ms_per_tick ÷ speed`. Speed comes from drone-speed upgrades and a
  UI speed slider (×1, ×4, ×16). There's also a "turbo" setting with no animation, available only after an upgrade.
  **Amended 2026-09-24 (user request):** no speed buttons or Turbo. Real-time speed comes only from Drone Speed
  upgrades, and the balance guarantees no upgrade (or computer) needs more than 5 minutes of waiting
  (enforced by `tests/test_progress.py`).
- **Floors**: each floor has its own `n × n` grid (it starts at 3, and grid upgrades apply per floor). The grid
  has walls (amended 2026-09-24, user request: no wrap-around). Moving into a wall leaves the drone in place,
  stuns it for 1 real second (`STUN_MS`, at every Drone Speed) and prints "Bonk!", and `move()` returns False.
  There's one drone. It has a position and a current floor.
- **Inventory**: one global dict of part → count.
- **Randomness**: seeded per save, so a replay is reproducible for tests.

### Drone API (each call costs ticks; available only once unlocked)

| Function | Unlock | Notes |
|---|---|---|
| `harvest()` | start | collects the part under the drone if it's ready |
| `move(dir)` | start | `North/East/South/West`. Walls: bumping one stuns for 1 s and returns False |
| `print(...)` | start | writes to the console (costs a few ticks, as in TFWR) |
| `can_harvest()` | Conditionals | whether the part under the drone is ready |
| `place(Part.X)` | CPU floor | starts building a part on an empty tile, paying its cost |
| `get_pos()` | Positions | returns an `(x, y)` **tuple** |
| `get_world_size()` | Positions | size of the current floor's grid |
| `num_items(Part.X)` | Variables | inventory count |
| `goto_floor(Floor.X)` | CPU floor | rides the lift (costs ticks) |
| `get_floor()` | CPU floor | current floor |
| `is_faulty()` | Motherboard floor | whether the board under the drone is faulty |
| `measure()` | GPU floor | benchmark score (0–9) of the GPU chip under the drone |
| `swap(dir)` | GPU floor | swaps this chip with its neighbour |
| `get_order()` | Final Assembly | the current order as a **dict**, e.g. `{Part.RAM: 4, Part.CPU: 2}` |
| `assemble()` | Final Assembly | fulfils the current order from inventory, earning Computers |
| `wait(ticks)` | Loops | lets time pass |

### Floors and puzzles

| Floor | Mechanic | Pressure on the player's code |
|---|---|---|
| **RAM** (start) | Every tile holds a stick that regrows a short time after harvesting. Harvesting before it's ready gives nothing | loops, `range`, sweeping the grid |
| **CPU** | Tiles start empty. `place(Part.CPU)` bakes for a random time. Harvesting early **destroys** the chip | `if can_harvest()`, variables |
| **SSD** | `place(Part.SSD)` costs RAM + CPU and yields several SSDs | operators, `num_items`, planning across floors |
| **Motherboard** | `place(Part.BOARD)` costs SSDs. About 20% of boards finish **faulty**. Harvesting a faulty board **raises `FaultyBoardError`**, which stops the program unless it's caught. A fully good `k × k` block merges into one big board worth `k³` | `is_faulty()` checks, lists/sets to remember positions, functions, then `try/except` |
| **GPU** | `place(Part.GPU)` gives a chip with a random score. Harvesting a fully **sorted** grid (rows increase east, columns increase north) pays `n²` per chip, while an unsorted harvest pays 1 | nested loops, a sorting algorithm with `swap` |
| **Final Assembly** | Orders arrive as dicts of parts. `assemble()` consumes them and pays 1 Computer, the top currency. Orders grow over time (amended: each order pays 1 computer; the win counts orders completed) | dicts, `for key, value in d.items()`, planning |

The exact numbers (tick costs, grow times, yields, prices) live in one data file (`src/python/game/balance.py`)
so they can be tuned in one place.

## Upgrade tree

Each unlock has a cost in parts, a list of prerequisites and a help page. Rough order, which the balance file can change:

1. **Loops** (`while True`, `while cond`) · **Speed I** · **Grid 4×4 (RAM)**
2. **Variables & operators** (assignment, `+ - * / // % **`, comparisons, `and/or/not`) · `num_items`
3. **Conditionals** (`if/elif/else`, `can_harvest`) → opens **CPU floor**
4. **for & range** · **Positions** (`get_pos` tuples, `get_world_size`) → tuples help page
5. **Functions** (`def`, parameters, `return`, defaults)
6. **SSD floor** · **Lists** · **Strings & f-strings**
7. **Motherboard floor** (`is_faulty`) · **Sets** · **Dictionaries**
8. **Comprehensions & lambda** · **Higher-order functions** (`map/filter/sorted`)
9. **GPU floor** (`measure`, `swap`)
10. **Modules**: extra code windows (files) that `import` each other
11. **Exceptions** (`try/except/else/finally`, `raise`) · error-types help page
12. **Final Assembly** (`get_order`, `assemble`)
13. **Classes** (`class`, `__init__`, methods, inheritance). Nothing forces them, but the Final Assembly help page
    suggests an `OrderPlanner` class, and there's an optional challenge
14. Throughout: Speed II–V and grid sizes up to 8×8 per floor (Turbo was removed, see the Pacing amendment)

Built-ins that come with each feature (`len`, `range`, `min`, `max`, `abs`, `str`, `int`, `list`, `dict`,
`set`, `sorted`…) are grouped with the unlock they belong to. The `math` and `random` imports
come with Modules.

### Feature gating

Before running, the player's code is parsed with Python's `ast` module. Each node type or built-in name maps to an unlock
(e.g. `While` → Loops, `FunctionDef` → Functions, `ListComp` → Comprehensions, `Try` → Exceptions,
`ClassDef` → Classes, `Import` → Modules). Anything locked is reported with its line number and the
unlock's name, and the code does not run.

## Architecture

- **Static site**: Vite + TypeScript + Preact, CodeMirror 6. Kept from v1.
- **Worker** (Pyodide from jsDelivr): holds the **world state and the player's program together**, so
  actions are plain synchronous function calls.
  - **Pacing**: an action calls a blocking wait. When the page is `crossOriginIsolated` this is
    `Atomics.wait` on a SharedArrayBuffer. Otherwise it falls back to a short busy-wait.
  - **Stop**: when isolated, Pyodide's **interrupt buffer** raises `KeyboardInterrupt` in the player's code,
    so the world stays in the worker. Otherwise the worker is terminated and rebuilt from the last snapshot.
  - **Cross-origin isolation on GitHub Pages** via `coi-serviceworker` (it adds COOP/COEP headers from a service
    worker). jsDelivr sends `Cross-Origin-Resource-Policy: cross-origin`. Google Fonts get dropped in favour of
    system fonts, to avoid problems with COEP.
  - **Snapshots**: after each action the worker posts a compact state diff (drone position and floor, changed tiles,
    inventory, clock). The main thread renders and keeps the latest full snapshot for saving.
- **Main thread**: renders the current floor (SVG grid, drone sprite, part states such as growing/ready/faulty and GPU
  scores), the inventory bar, code windows (tabs = files), Run/Stop, the speed slider, the console, the upgrade tree
  panel and help pages. Unlock purchases happen on the main thread while no program is running, and are sent to the worker.
- **Python package** `src/python/game/`: `world.py` (floors, tiles, clock, rules), `api.py` (functions the player
  calls), `gating.py` (AST checks), `balance.py` (all numbers), `unlocks.py` (the tree), `runner.py` (sets up
  the namespace and files, runs, and gives friendly errors reusing v1's `friendly_error`).
- **Save** (`byteworks.save.v2`): world state, unlocks, code files and settings. Autosaved after each run and
  purchase, plus the export/import save code. v1 saves are ignored.

## What v1 code is reused / removed

- **Reused**: the Pyodide worker/runner skeleton, the timeout logic (used only as a watchdog now), save/save-code
  handling, friendly error messages, the floor lift UI, the CodeMirror editor, styles, the deploy workflow, and lesson text
  (rewritten into short help pages, with the "Try it" run boxes kept).
- **Removed**: `src/levels/day*`, the level checker, the v1 simulated modules (web, mongo, pip, venv),
  `tests/run_levels.py`.

## Testing

- **Python game logic under CPython** (`tests/test_game.py`, unittest): tick costs, growth, faulty boards and
  merging, GPU sort detection, orders, lift, gating (locked constructs rejected with the right line), and
  determinism with a fixed seed.
- **"Reference bots"**: short example programs for each stage (e.g. a RAM sweeper, a CPU farmer, a board
  fixer, a GPU bubble sort, an order filler). Tests run them headless (no pacing) and check they earn
  enough to afford the next unlocks. This checks the game can be completed and that the economy is balanced.
- **Vitest**: save encode/decode and v2 validation, unlock-tree prerequisites.
- **Browser check (Chrome)**: run/stop a `while True` farm, buy an unlock, change floors, locked-feature message,
  reload keeps progress, and the production build works with the service worker.

## Open questions (fine to decide during implementation)

- Exact balance numbers. Tuned using the reference bots so that finishing takes a few hours, not days.
- Whether multiple drones (TFWR's late game) are added later. Out of scope for this version.
