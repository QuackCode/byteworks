# Conditionals

Harvesting a RAM stick that hasn't regrown wastes time. **Conditionals** let your code decide what to do.

## `if`

```python
temp = 95
if temp > 90:
    print("Too hot!")
print("This line always runs")
```

The indented lines only run when the condition is `True`.

## `else` and `elif`

```python
clock = 3.2
if clock >= 4.0:
    kind = "fast"
elif clock >= 2.5:
    kind = "medium"
else:
    kind = "slow"
print(kind)
```

Python checks each condition **from top to bottom** and runs **only the first** one that's `True`, so the order matters.

## One-line version

```python
temp = 50
status = "hot" if temp > 90 else "ok"
print(status)
```

## The drone's senses

| Function | Gives back |
|---|---|
| `can_harvest()` | `True` if the part under the drone is ready |
| `get_part()` | the part under the drone, like `"RAM"`, or `None` for an empty tile |

Checking is almost free: it takes 1 tick, while a wasted harvest takes 100.

```py
row = 0
while True:
    if can_harvest():
        harvest()
    if row < 2:
        move(North)
        row = row + 1
    else:
        move(South)
        move(South)
        row = 0
```

## Try this

Turn this into a whole-floor snake route: after each column, step East instead of going back down. Then compare how much RAM you get per minute with and without `can_harvest()`.
