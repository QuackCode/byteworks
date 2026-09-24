# Loops

Pressing **Run** over and over is tiring. A **loop** repeats code for you, so your drone can work all day.

## `while True:` means keep going forever

```py
while True:
    harvest()
    move(North)
```

- `while` is followed by a **condition** and a colon `:`
- The **indented** lines (4 spaces) are the loop's body. They repeat
- `True` is always true, so this loop never ends on its own. That's normal in ByteWorks: press **■ Stop** when you want it to finish

Python only knows what's *inside* the loop by the indentation. When the indentation stops, the loop body is over.

## Sweeping more of the floor

The floor wraps round, so moving North three times on a 3×3 floor brings you back to where you started. Add a `move(East)` to shift to the next column each time round:

```py
while True:
    harvest()
    move(North)
    harvest()
    move(North)
    harvest()
    move(North)
    move(East)
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

## Try this

Write a loop that sweeps the whole 3×3 RAM floor forever. Then speed it up with the **x4** button.
