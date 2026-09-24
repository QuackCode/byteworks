# Loops

Pressing **Run** over and over is tiring. A **loop** repeats code for you, so your drone can work all day.

## `while True:` means keep going forever

```py
while True:
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(South)
    move(South)
```

- `while` is followed by a **condition** and a colon `:`
- The **indented** lines (4 spaces) are the loop's body. They repeat
- `True` is always true, so this loop never ends on its own. That's normal in ByteWorks: press **■ Stop** when you want it to finish

Python only knows what's *inside* the loop by the indentation. When the indentation stops, the loop body is over.

## Sweeping more of the floor

Watch out for the walls: on a 3×3 floor, a third `move(North)` in a row walks into the wall and stuns the drone. So go up the first column, step East, come down the next one, and so on (a **snake** route), then walk back to the corner so the loop can start again:

```py
while True:
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
    move(West)
    move(West)
    move(South)
    move(South)
```

## `break` and `continue`

- `break` stops the loop completely, right now
- `continue` skips the rest of this go and starts the next one

```python
while True:
    print("This runs once")
    break
print("...then the loop is over")
```

You'll use these more once you unlock **Conditionals** and can decide *when* to break.

## `wait(ticks)`

Sometimes the best thing to do is nothing. `wait(100)` lets 100 ticks of game time pass, which gives RAM time to regrow:

```py
while True:
    harvest()
    wait(300)
```

## 🎯 Quest

**Use a loop to sweep the floor twice in one run: 18 RAM with zero bonks.** Doing it lets you buy **Variables & Operators** (you'll still need its parts).

Put a whole snake route inside `while True:`, press Run, and let it go round twice. A single bonk spoils it, so check your route first.
