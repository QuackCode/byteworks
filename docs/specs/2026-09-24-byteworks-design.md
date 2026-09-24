# ByteWorks — learn Python by running a computer factory

## Context
Nathan wants a new project that teaches Python to complete beginners, covering everything in
Asabeneh's *30 Days of Python* as a step-by-step tutorial. The hook: you run a factory that builds
computers, and every Python concept is a job on the factory floor (a `while` loop keeps a machine
running, a `try/except` stops a faulty motherboard from crashing the line). Later parts add
challenges such as random faulty parts that the learner's code must detect.

Decisions made with the user:
- **Browser game**, continuous, **free to host**, ~30 concurrent players.
- **Complete beginners**: explanations assume nothing.
- **One growing factory**: machines built in earlier shifts persist and feed later ones; by Day 30 a
  whole computer is assembled.
- **Progress saved in the browser** (localStorage), plus an export/import save code. No accounts.
- Days that can't run in a browser (scraping, venv, Flask, MongoDB, APIs) are **simulated in-factory**.

**Privacy constraint:** create only `~/projects/byteworks/`. Do NOT list, read or touch anything
else in `~/projects`.

## Architecture
Static site, so hosting is free and scales to any number of players (all Python runs client-side).

- **Stack:** Vite + TypeScript + Preact (small, simple), CodeMirror 6 editor (Python mode).
- **Python runtime:** Pyodide loaded from the jsDelivr CDN, running in a **Web Worker**.
  - Infinite-loop protection: a run timeout (e.g. 5s). On timeout the worker is terminated and
    respawned, and the player sees "The machine overheated! Your loop never stopped."
    (Needed because `while` loops are taught. Avoids SharedArrayBuffer, which GitHub Pages can't enable.)
- **`factory` Python module**: injected into Pyodide. The learner's code talks to it
  (`belt.next_part()`, `assembler.install(part)`, `qc.reject(board)` …). Every call is written to an
  event log that is returned to JS and animated.
- **Level checker:** each level ships a Python `check()` that runs the learner's code against
  several **seeded** scenarios (e.g. seeds where motherboard #7 and #13 are faulty). It returns
  pass/fail, a friendly message per failure, and the event log. Seeded randomness keeps runs
  reproducible and stops hard-coded answers.
- **Floors:** the factory is a building with **one floor per computer part**. Each floor has its own
  full screen (SVG) with its machines and belts, and ▲/▼ arrows (plus keyboard ↑/↓) move between
  floors. A small elevator indicator shows the current floor. Locked floors appear greyed out
  ("Floor locked: finish Day N"). Parts move along belts while events replay (built ✓,
  rejected ✗, crashed 💥). Finished floors keep running idle animations, and their output ships
  upstairs to the Final Assembly floor.
- **Save system:** localStorage (`byteworks.save.v1`: completed days, the learner's code per day,
  factory state), with a base64 export/import code. Reads/writes are wrapped in try/catch.
- **Hosting:** GitHub Pages deployed by a GitHub Actions workflow (Cloudflare Pages also works).
  It's served from GitHub's servers around the clock, so Nathan's laptop never needs to be on.
  Pushing to `main` redeploys the site. The README gives step-by-step setup.

### Project layout
```
~/projects/byteworks/
  index.html, vite.config.ts, package.json, README.md
  docs/specs/2026-09-24-byteworks-design.md   # this design, committed first
  src/
    main.tsx, app/ (screens: Map, Shift, Lesson, Settings)
    engine/ pyodideWorker.ts, runner.ts (timeout/respawn), save.ts
    factory/ view (SVG floor + animation), events.ts
    python/ factory/  (the injected Python package: belt, machines, qc, fakes for days 22–29)
    levels/ day01.ts … day30.ts   # data: story, lesson markdown, starter code, hints, check.py, solution
  tests/ levels.test.ts (vitest + pyodide in node), e2e smoke (Playwright)
  .github/workflows/deploy.yml
```

## Level anatomy (every day)
1. **Shift briefing:** a short story from the foreman about what's broken or needed.
2. **Lesson:** a beginner explanation with runnable mini examples ("Try it" boxes).
3. **Task:** starter code with clearly marked gaps, plus 3 progressive hints (the last one is nearly the answer).
4. **Run:** the factory animates the result. The checker explains failures in plain English.
5. **Bonus challenge (optional):** a harder variant for fast learners.
6. Passing unlocks the next day and adds or upgrades a machine on the factory map.

## Curriculum → factory mapping (30 shifts)
| Floor | Day | Topic | Factory job |
|---|---|---|---|
| **G: Control Room** | 1 | Intro, `print`, comments | Power on the factory and print the boot message |
| | 2 | Variables, built-in functions | Name machines, set speeds, `len`/`type` config |
| | 3 | Operators | Throughput, costs and power draw; comparisons for thresholds |
| | 4 | Strings | Serial-number labels, f-strings, slicing part codes |
| **1: RAM** | 5 | Lists | The RAM conveyor is a list: append, pop, sort, index |
| | 6 | Tuples | Fixed RAM stick specs (capacity, speed) that must never change |
| | 7 | Sets | Duplicate RAM serials; set operations on supplier stocks |
| | 8 | Dictionaries | RAM warehouse inventory |
| **2: CPU** | 9 | Conditionals | First QC: bin CPUs by clock speed; faulty chips start appearing |
| | 10 | Loops | `while` keeps the CPU press running; `for` walks the belt; break/continue |
| | 11 | Functions | `build_cpu()` and reusable machine routines |
| | 12 | Modules | `import random/math`; your own `qc` module |
| **3: Storage (SSD)** | 13 | List comprehension | Filter a batch of dead SSDs in one line |
| | 14 | Higher-order functions | map/filter/reduce, lambdas, a logging decorator on machines |
| | 15 | Python error types | Read crash reports (TypeError, KeyError…) and fix the line |
| | 16 | datetime | Timestamps, SSD shift schedules, delivery deadlines |
| **4: Motherboard** | 17 | Exception handling | Faulty boards raise errors; `try/except` keeps the line alive |
| | 18 | Regular expressions | Validate board serials and spot counterfeit chips |
| | 19 | File handling | Read order files, write production logs (Pyodide virtual FS) |
| | 20 | PIP | A real `micropip` install of a helper package |
| | 21 | Classes & objects | `Machine`, `Motherboard`, inheritance (`BoardTester(Machine)`) |
| **5: GPU** | 22 | Web scraping (sim) | Parse the supplier's catalogue HTML for GPU chip prices |
| | 23 | Virtual environments (sim) | Isolated GPU workshops with their own requirements |
| | 24 | Statistics (numpy) | GPU defect rates, mean/std of benchmark scores |
| | 25 | Pandas | Weekly GPU production reports from a DataFrame |
| **6: Shipping & Orders** | 26 | Python for web (sim) | A Flask-like fake framework: route order pages with `@app.route` |
| | 27 | MongoDB (sim) | A pymongo-like fake order DB: `insert_one`, `find`, `update_one` |
| | 28 | APIs (sim) | Call the courier API (fake `requests.get` → JSON) |
| | 29 | Building an API (sim) | The factory's own order API (CRUD handlers) |
| **7: Final Assembly** | 30 | Final shift | Boss level: pull parts from every floor and build a full computer, with faults at every stage |

Challenge escalation: from Day 9, belts carry seeded random defects. Day 17 onward the faults raise
exceptions. Day 30 combines everything. Machines unlocked earlier are reused (for example, the Day 11
`build_cpu()` feeds the Day 21 assembler).

## Build phases
1. Scaffold, write the spec into `docs/specs/`, `git init`, engine (worker, runner, timeout, save),
   factory view, level framework, and **Days 1–10 playable**.
2. Days 11–21.
3. Days 22–30 (fake scraping/DB/web/API modules, numpy/pandas via Pyodide), deploy workflow, README
   with hosting steps.

## Verification
- `npm run build` succeeds.
- `npm test` (vitest, Pyodide in Node): for every day, the **reference solution passes** the checker
  and the **untouched starter code fails** with a friendly message. Seeded fault scenarios are covered.
- An infinite-loop test: `while True: pass` times out and the worker recovers.
- A Playwright smoke test: load the site, complete Day 1, reload, and confirm progress persists;
  ▲/▼ floor navigation works and locked floors can't be entered; export/import the save code.
- Manual check with `npm run dev` in the browser: play through Days 1, 10, 17 and 30.
