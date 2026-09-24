## Lists: many values in one variable

A **list** holds several values in order, inside square brackets `[]` and separated by commas:

```python
belt = ["RAM-01", "RAM-02", "RAM-03"]
print(belt)
print(len(belt))        # 3 items
empty = []              # an empty list
mixed = ["RAM", 32, True, 5.5]   # a list can hold any types
print(mixed)
```

## Indexing and slicing work just like strings

```python
belt = ["RAM-01", "RAM-02", "RAM-03", "RAM-04"]
print(belt[0])      # RAM-01  (first: counting starts at 0!)
print(belt[-1])     # RAM-04  (last)
print(belt[1:3])    # ['RAM-02', 'RAM-03']
```

**But** unlike strings, lists are **mutable**, which means you can change them:

```python
belt = ["RAM-01", "RAM-02"]
belt[0] = "RAM-99"    # replace an item
print(belt)
```

## Checking what's on the belt

```python
belt = ["RAM-01", "RAM-02"]
print("RAM-02" in belt)       # True
print(belt.index("RAM-02"))   # 1  (its position)
```

## List methods

| Method | What it does |
|---|---|
| `belt.append(x)` | add `x` to the **end** |
| `belt.insert(i, x)` | add `x` at position `i` |
| `belt.remove(x)` | remove the first item equal to `x` |
| `belt.pop()` | remove the **last** item and give it back |
| `belt.pop(i)` | remove the item at position `i` and give it back |
| `belt.sort()` | sort the list (A→Z, small→big) **in place** |
| `belt.reverse()` | reverse the order in place |
| `belt.count(x)` | how many times `x` appears |
| `belt.copy()` | make a separate copy |
| `belt.clear()` | empty the list |
| `del belt[i]` | delete the item at position `i` |

```python
belt = ["RAM-03", "RAM-01"]
belt.append("RAM-02")
print(belt)                 # ['RAM-03', 'RAM-01', 'RAM-02']
first = belt.pop(0)
print(first, belt)          # RAM-03 ['RAM-01', 'RAM-02']
belt.sort()
print(belt)
```

⚠️ `.sort()` changes the list and gives back **nothing** (`None`), so write `belt.sort()`, **not** `belt = belt.sort()`!

Join two lists with `+`: `[1, 2] + [3]` gives `[1, 2, 3]`. Unpack items into variables: `a, b = ["x", "y"]`.

## Your task

You're given `belt` (a list of RAM serials), `new_stick` and `faulty_stick`. Do these **in order**:

1. Add `new_stick` to the end of the belt
2. Remove `faulty_stick` from the belt
3. Take the **first** stick off the belt and store it in `tester`
4. Sort the belt
5. `count`: how many sticks are left
6. `first_on_belt` and `last_on_belt`: the first and last sticks now on the belt
