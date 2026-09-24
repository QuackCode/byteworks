# 🏭 ByteWorks

**Learn Python by programming a drone to rebuild a computer factory.** A free browser game in the style of
*The Farmer Was Replaced*. You write real Python, watch your drone carry it out live, earn computer parts,
and spend them on upgrades that unlock new Python features, faster drones, bigger floors and new factory floors.

## How to play

1. Write code in the editor (`harvest()`, `move(North)`, …) and press **▶ Run** (or Ctrl + Enter).
2. The drone does exactly what you wrote. A `while True:` loop keeps it going until you press **■ Stop**.
3. Parts you harvest are money. Open **⬆️ Upgrades** to buy new Python features, speed, grid sizes and floors.
4. Every unlock opens a **📖 Help** page with a beginner explanation and "Try it" examples.
   Each new Python feature also needs that page's **🎯 quest** (e.g. "sweep the floor twice with zero bonks"),
   checked automatically from what your program actually did.
5. The goal: build **10 complete computers** at Final Assembly.

| Floor | Puzzle |
|---|---|
| 🧠 RAM | sticks regrow a moment after you harvest them |
| 🔲 CPU | `place()` chips and let them bake. Harvest too early and they're destroyed |
| 💾 SSD | cost RAM + CPUs to build, so plan across floors |
| 🟩 Motherboard | about 1 in 5 boards come out **faulty**, and harvesting one crashes your program. A full square of good boards merges into a big one worth size³ |
| 🎮 GPU | chips have scores. Sort the whole grid with `swap()` for a huge bonus |
| 🖥️ Final Assembly | fill customer orders (dictionaries of parts) to build computers |

## What you learn

Covers the core of [30 Days of Python](https://github.com/Asabeneh/30-Days-Of-Python): comments & print → loops →
variables & operators → conditionals → for & range → tuples → functions → lists → strings & f-strings → sets →
dictionaries → comprehensions & lambda → higher-order functions → modules (several code windows that import each
other) → error types & exceptions → classes.

## How it works

- **Python runs in the player's browser** with [Pyodide](https://pyodide.org), in a Web Worker that holds the whole
  factory **and** runs the player's program. Each drone action advances a game clock, then waits in real time
  (`Atomics.wait`) so you can watch it happen.
- **Stop** uses Pyodide's interrupt buffer. If the page isn't cross-origin isolated, the game falls back to
  busy-waiting, and Stop restarts the worker from the latest saved state.
- **GitHub Pages can't set headers**, so `public/coi-serviceworker.min.js` adds the cross-origin isolation headers.
- **Locked features**: before running, the code is checked with Python's `ast` module, and anything not yet unlocked
  is reported with its line number.
- **Progress saves in the browser** (localStorage). The 💾 Save button gives a save code for moving it to another device.
- There's no server, so hosting is free and any number of people can play at once.

## Put it online (free, runs 24/7, your computer can be off)

1. Create a new repository on GitHub (e.g. `byteworks`) and push this folder to it:
   ```sh
   git remote add origin https://github.com/<your-username>/byteworks.git
   git push -u origin main
   ```
2. On GitHub, open **Settings → Pages** and set **Source** to **GitHub Actions**.
3. The workflow in `.github/workflows/deploy.yml` runs the tests, builds the site and publishes it.
   After a minute or two the game is live at `https://<your-username>.github.io/byteworks/`.

Every later push to `main` updates the site automatically.

## Run it locally

```sh
npm install
npm run dev          # open the address it prints
```

## Tests

```sh
npm test
```

This runs the vitest unit tests, the Python game-rule tests, a check that every help-page example works (and only
uses features unlocked at that point), and a **full playthrough by reference bots** that proves the game can be
finished.

## Project layout

```
src/python/game/   the whole game in Python: world rules, upgrade tree, feature gating, player API, runner
src/engine/        Pyodide worker, GameRunner (pacing, Stop, restarts), save format
src/app/           the Preact UI: floors + drone, code windows, console, upgrades, help
src/help/*.md      one help page per unlock (python blocks = runnable, py blocks = drone examples)
tests/             Python unit tests, help-page tests, reference bots + playthrough, vitest
```

## Tuning the game

All the numbers (tick costs, grow times, yields, prices, order sizes) live in `src/python/game/balance.py`, and
upgrade costs live in `src/python/game/unlocks.py`. After a change, run

```sh
python3 -m unittest tests.test_progress -v
```

It prints how long the reference bots take, and **fails if any upgrade (or any computer at the end) needs more than 5 minutes of waiting**. There's no fast-forward button, so this keeps the game moving.

---

Curriculum based on *30 Days of Python* by Asabeneh Yetayeh. Game idea inspired by *The Farmer Was Replaced*.
