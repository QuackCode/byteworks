# 🏭 ByteWorks

**Learn Python by rebuilding a computer factory.** A free browser game that teaches complete beginners
everything in [30 Days of Python](https://github.com/Asabeneh/30-Days-Of-Python), one factory shift at a time.

Each floor of the factory builds a different computer part. Every day you learn a new Python idea and
use it to get a machine running: a `while` loop keeps the CPU press going, `try/except` stops a faulty
motherboard from crashing the line, pandas prints the weekly GPU report. On Day 30 you put it all
together and ship finished computers.

| Floor | Days | Topics |
|---|---|---|
| G · Control Room | 1–4 | print, variables, operators, strings |
| 1 · RAM | 5–8 | lists, tuples, sets, dictionaries |
| 2 · CPU | 9–12 | conditionals, loops, functions, modules |
| 3 · Storage | 13–16 | comprehensions & lambdas, higher-order functions, error types, datetime |
| 4 · Motherboard | 17–21 | exception handling, regex, file handling, pip, classes |
| 5 · GPU | 22–25 | web scraping, virtual environments, NumPy, pandas |
| 6 · Shipping & Orders | 26–29 | Flask, MongoDB, using APIs, building an API |
| 7 · Final Assembly | 30 | the boss level: everything together |

## How it works

- **Python runs in the player's browser** using [Pyodide](https://pyodide.org) (in a Web Worker).
  There's no server, so hosting is free and any number of people can play at once.
- **Infinite loops can't freeze the page.** Runs time out after 6 seconds, and Python restarts.
- **Each level is checked by Python code** (`check.py`) that runs the player's code against several
  *seeded* random scenarios. Faulty parts appear in different places each test, so hard-coded
  answers don't pass. Failures are explained in plain English.
- **Progress saves in the browser** (localStorage). The 💾 Save button gives a save code for moving
  progress to another device.
- Things a browser can't really do are **simulated** with factory-themed fakes that behave like the
  real libraries: `pip`, virtual environments, `requests` (the websites and APIs), `flask` and `pymongo`.
  NumPy, pandas and BeautifulSoup are the real thing.

## Put it online (free, runs 24/7, your computer can be off)

1. Create a new repository on GitHub (e.g. `byteworks`) and push this folder to it:
   ```sh
   git remote add origin https://github.com/<your-username>/byteworks.git
   git push -u origin main
   ```
2. On GitHub, open **Settings → Pages** and set **Source** to **GitHub Actions**.
3. The workflow in `.github/workflows/deploy.yml` tests the levels, builds the site and publishes it.
   After a minute or two the game is live at `https://<your-username>.github.io/byteworks/`.

Every later push to `main` updates the site automatically.

## Run it on your computer

```sh
npm install
npm run dev          # open the address it prints
```

## Tests

```sh
npm run setup:py     # once: a .venv with numpy, pandas and bs4 for the level tests
npm test             # unit tests + every level: solution passes, starter code fails
npm run build        # production build into dist/
```

## Project layout

```
src/
  app/            the website (Preact): floors, lift, lessons, editor, save dialog
  engine/         Pyodide worker, runner (timeouts), save + progress logic
  python/factory/ the Python package the levels use: checker, machines, simulated pip/web/mongo
  levels/dayNN/   one folder per day:
    meta.json       title, floor, briefing, 3 hints, bonus challenge
    lesson.md       the lesson (```python blocks become runnable "Try it" boxes)
    starter.py      the code the player starts with (blanks are ____)
    solution.py     a reference answer (never shown to players)
    check.py        setup(world) gives the player their data; check(ctx) tests their code
tests/            vitest unit tests + tests/run_levels.py
```

### Adding or changing a level

Edit the files in `src/levels/dayNN/`, then run `npm run test:levels`. It checks that the solution
passes and the starter code fails with a message. In `check.py`, `ctx.run(seed)` runs the player's
code, `ctx.expect(condition, "friendly message")` tests it, and `ctx.show("part", label=..., result="ship")`
animates parts on the factory floor.

---

Curriculum based on *30 Days of Python* by Asabeneh Yetayeh.
