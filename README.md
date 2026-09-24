# 🏭 ByteWorks

**Learn Python by programming a drone to rebuild a computer factory.** A free browser game in the style of
*The Farmer Was Replaced*. You write real Python, watch your drone carry it out live, earn computer parts,
and spend them on upgrades that unlock new Python features, faster drones, bigger floors and new factory floors.

## How to play

1. Write code in the editor (`harvest()`, `move(North)`, …) and press **▶ Run** (or Ctrl + Enter).
2. The drone does exactly what you wrote. A `while True:` loop keeps it going until you press **■ Stop**.
3. Parts you harvest are money. Open **Upgrades** to buy new Python features, speed, grid sizes and floors.
4. Every unlock opens a **Help** page with a beginner explanation and "Try it" examples.
   Each new Python feature also needs that page's **quest** (e.g. "sweep the floor twice with zero bonks"),
   checked automatically from what your program actually did.
5. The goal: build **10 complete computers** at Final Assembly.

| Floor | Puzzle |
|---|---|
| RAM | sticks regrow a moment after you harvest them |
| CPU | `place()` chips and let them bake. Harvest too early and they're destroyed |
| SSD | cost RAM + CPUs to build, so plan across floors |
| Motherboard | about 1 in 5 boards come out **faulty**, and harvesting one crashes your program. A full square of good boards merges into a big one worth size³ |
| GPU | chips have scores. Sort the whole grid with `swap()` for a huge bonus |
| Final Assembly | fill customer orders (dictionaries of parts) to build computers |

## What you learn

Covers the core of [30 Days of Python](https://github.com/Asabeneh/30-Days-Of-Python): comments & print → loops →
variables & operators → conditionals → for & range → tuples → functions → lists → strings & f-strings → sets →
dictionaries → comprehensions & lambda → higher-order functions → modules (several code windows that import each
other) → error types & exceptions → classes.

---

Curriculum based on *30 Days of Python* by Asabeneh Yetayeh. Game idea inspired by *The Farmer Was Replaced*.
