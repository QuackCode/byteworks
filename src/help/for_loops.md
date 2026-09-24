# For Loops & range

A `while` loop needs a counter to stop after 3 goes. A `for` loop does the counting for you.

## `for` walks through things

```python
for name in ["RAM", "CPU", "SSD"]:
    print("Visiting", name)
for letter in "BYTE":
    print(letter)
```

## `range()` makes numbers

`range` stops **before** the end number, just like slicing:

```python
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)
for i in range(1, 4):       # 1, 2, 3
    print("Lap", i)
for i in range(10, 0, -3):  # 10, 7, 4, 1
    print(i)
```

## Loops inside loops

The inner loop runs completely for **each** go of the outer loop:

```python
for row in "AB":
    for col in range(1, 4):
        print(row + str(col))
```

That's exactly how you sweep a grid: go North through a column, then step East, over and over.

```py
while True:
    for col in range(3):
        for row in range(3):
            if can_harvest():
                harvest()
            if row < 2:
                if col % 2 == 0:
                    move(North)
                else:
                    move(South)
        if col < 2:
            move(East)
    move(West)
    move(West)
    move(South)
    move(South)
```

## Extras

- `break` and `continue` work in `for` loops too
- `pass` means "do nothing" (a placeholder)
- A `for` loop can have an `else:` that runs if the loop finished without a `break`

```python
for n in [1, 2, 3]:
    pass
else:
    print("Loop finished without a break")
```

## 🎯 Quest

**Sweep with for loops: harvest 18 parts in one run with zero bonks.** Doing it lets you buy **Positions & Tuples** (you'll still need its parts).

Use `for lap in range(2):` around a snake route built from two nested `for` loops.
