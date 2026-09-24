# Positions & Tuples

## Tuples: values that belong together

A **tuple** is like a list that can **never be changed**. It uses round brackets:

```python
spot = (2, 1)
print(spot[0], spot[1])   # indexing works like lists
print(len(spot))
```

Use tuples for things that belong together and shouldn't change, like a position `(x, y)` or a date `(2026, 9, 24)`. Trying to change one is an error: `spot[0] = 5` gives a `TypeError`.

A one-item tuple needs a comma: `(5,)`. Without it, `(5)` is just the number 5.

## Unpacking

Pull a tuple's values into separate variables in one line:

```python
spot = (2, 1)
x, y = spot
print("x is", x, "and y is", y)
```

## Tuple tools

```python
spots = ((0, 0), (1, 2), (0, 0))
print(spots.count((0, 0)))   # 2
print(spots.index((1, 2)))   # 1
print((1, 2) in spots)       # True
```

## Where is the drone?

- `get_pos()` gives the drone's position as an `(x, y)` tuple. `(0, 0)` is the bottom-left corner, North is +y and East is +x
- `get_world_size()` gives how many squares wide the current floor is

```py
x, y = get_pos()
print("Drone at", x, y)
size = get_world_size()
for col in range(size):
    for row in range(size):
        if can_harvest():
            harvest()
        if row < size - 1:
            if col % 2 == 0:
                move(North)
            else:
                move(South)
    if col < size - 1:
        move(East)
```

Using `get_world_size()` means your sweep keeps working when you buy a bigger grid.

## Try this

Write code that moves the drone back to `(0, 0)` from wherever it is.
