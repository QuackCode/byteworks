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

Press **▶ Run** (or **Ctrl + Enter**) and watch the drone.

## Mind the walls! 💫

Every floor has walls round the edge. If the drone tries to move into a wall, it **bonks**: it stays where it is and is **stunned for 1 second**. Every bonk costs another second, so plan a route that turns round before the edge instead of charging into it. The drone starts in the bottom-left corner.

## Comments

A line starting with `#` is a **comment**. Python skips it, so it's a note for humans:

```python
# This line is ignored
print("This line runs")  # comments can go at the end of a line too
```

## Code windows

Click **+ New window** above the editor to make extra programs, like one for each floor. **▶ Run** runs the window that's open. The ✎ button renames a window and ✕ deletes it.

## Things take time

Every action takes a moment of game time. A RAM stick needs a little while to **regrow** after you harvest it. Harvest too soon and you get nothing.

## Upgrades

Parts are money. Open **⬆️ Upgrades** to spend them. Your first goal is **Loops (5 RAM)**. With loops, the drone can work forever without you pressing Run again. Each upgrade teaches a new bit of Python, and you'll find its page here in Help.

Every new Python feature also needs a **🎯 quest**: a small task from the help page you read before it. The game checks your runs automatically and shows 🏆 in the Console when you've done one. Your first quest is at the bottom of this page.

## 🎯 Quest

**Harvest all 9 RAM sticks in one run.** Doing it lets you buy **Loops** (you'll still need its parts).

Plan a route that visits every square without bonking a wall: nine `harvest()` calls, with moves in between.
