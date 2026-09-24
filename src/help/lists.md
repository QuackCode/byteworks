# Lists

A **list** holds many values in order, inside square brackets:

```python
belt = ["RAM-01", "RAM-02", "RAM-03"]
print(belt, len(belt))
print(belt[0], belt[-1])   # first and last (counting starts at 0!)
print(belt[1:3])           # slicing
```

Lists are **mutable**, which means you can change them:

```python
belt = ["RAM-01", "RAM-02"]
belt[0] = "RAM-99"
belt.append("RAM-03")
print(belt)
```

## List methods

| Method | What it does |
|---|---|
| `belt.append(x)` | add `x` to the end |
| `belt.insert(i, x)` | add `x` at position `i` |
| `belt.remove(x)` | remove the first `x` |
| `belt.pop()` / `belt.pop(i)` | remove and give back the last item / item `i` |
| `belt.sort()` / `belt.reverse()` | sort / reverse in place |
| `belt.index(x)` / `belt.count(x)` | position of `x` / how many times it appears |
| `belt.copy()` / `belt.clear()` | copy / empty |

```python
nums = [5, 2, 9]
nums.sort()
print(nums, 9 in nums, nums + [10])
```

⚠️ `.sort()` changes the list and gives back `None`, so write `nums.sort()`, not `nums = nums.sort()`.

## A list of floors to visit

```py
floors = [Floor.RAM, Floor.CPU, Floor.SSD]
while True:
    for f in floors:
        goto_floor(f)
        for col in range(3):
            for row in range(3):
                if can_harvest():
                    harvest()
                if get_part() == None:
                    place(f)
                move(North)
            move(East)
```

`Floor.CPU` and `Part.CPU` are the same text (`"CPU"`), so a floor name works as the part to place.

## Try this

Keep a list of how much RAM you had after each lap, and print it every 5 laps.
