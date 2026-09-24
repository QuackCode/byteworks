## Loops: doing things again and again

A factory doesn't build one chip, it builds thousands. **Loops** repeat code so you don't have to write it a thousand times.

## The `while` loop

`while` repeats its indented block **as long as its condition is True**:

```python
chips_left = 3
while chips_left > 0:
    print("Stamping... chips left:", chips_left)
    chips_left -= 1
print("Done!")
```

⚠️ If the condition never becomes False, the loop runs **forever**: an *infinite loop*. (In ByteWorks, the machine overheats and stops after a few seconds.) Always make sure something inside the loop moves it towards finishing.

## The `for` loop

`for` walks through each item in a collection (a list, string, tuple, set or dict), one at a time:

```python
belt = ["CPU-01", "CPU-02", "CPU-03"]
for chip in belt:
    print("Testing", chip)
```

```python
for letter in "RAM":
    print(letter)
stock = {"DDR4": 10, "DDR5": 25}
for model, count in stock.items():
    print(model, "→", count)
```

## `range()`: counting

`range()` makes a sequence of numbers. Like slicing, it stops **before** the end number:

```python
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)
for i in range(1, 4):       # 1, 2, 3
    print("Shift", i)
for i in range(10, 0, -3):  # 10, 7, 4, 1  (step of -3)
    print(i)
```

## `break` and `continue`

- `break`: **stop the loop completely**, right now
- `continue`: **skip the rest of this go** and jump to the next one

```python
for temp in [50, 60, 0, 70, 130, 80]:
    if temp == 0:
        print("  sensor glitch, skipping")
        continue
    if temp > 100:
        print("  EMERGENCY STOP!")
        break
    print("Temp OK:", temp)
```

Notice that 80 is never checked: `break` ended the loop at 130.

## Building a list with a loop

A very common pattern: start with an empty list and `append` to it as you go.

```python
evens = []
for n in range(10):
    if n % 2 == 0:
        evens.append(n)
print(evens)
```

## Extras: nested loops, `else` and `pass`

```python
for row in "AB":
    for col in range(1, 3):
        print(row + str(col), end=" ")   # a loop inside a loop
print()
for n in [1, 2]:
    pass            # pass means "do nothing": a placeholder
else:
    print("A for loop's else runs if the loop finished without a break")
```

## Your task

You control `press`, a machine with two methods:
- `press.has_power()` gives `True` while the press still has power
- `press.stamp()` makes one CPU and gives it back as a dict like `{"serial": "CPU-0401", "clock_ghz": 3.6, "temp_c": 55}`

1. Print a countdown `3`, `2`, `1` using a `for` loop with `range()`
2. **While** the press has power, stamp a chip and:
   - if its `temp_c` is **over 100**: print a warning and **stop the press** (`break`)
   - if its `clock_ghz` is `0` it's dead: add 1 to `dead` and skip it (`continue`)
   - otherwise add it to the `good` list
3. Finally, use a `for` loop to print the serial of every good chip
