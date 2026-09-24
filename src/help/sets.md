# Sets

A **set** is a collection where every item is **unique** and there's **no order**:

```python
models = {"DDR4", "DDR5", "DDR4", "DDR4"}
print(models, len(models))       # the duplicates vanished
unique = set(["A", "B", "A"])
print(unique)
```

⚠️ An empty set is `set()`, because `{}` makes an empty **dictionary**.

Sets have no positions (`models[0]` doesn't work), but checking membership with `in` is very fast.

## Changing a set

```python
stock = {"DDR4"}
stock.add("DDR5")
stock.update(["LPDDR5", "DDR3"])
stock.discard("DDR3")      # no error if it's missing
print(stock, "DDR5" in stock)
```

## Set maths

| Operation | Operator | Gives you |
|---|---|---|
| union | `a \| b` | everything in either |
| intersection | `a & b` | only what's in both |
| difference | `a - b` | in `a` but not `b` |
| symmetric difference | `a ^ b` | in one but not both |

```python
a = {"RAM", "CPU", "SSD"}
b = {"CPU", "GPU"}
print(a | b, a & b, a - b, a ^ b)
```

## Remembering which floors are done

```py
floors = [Floor.RAM, Floor.CPU, Floor.SSD]
visited = set()
for f in floors:
    goto_floor(f)
    harvest()
    visited.add(f)
print(visited)
```

## Try this

Use a set to count how many **different** floors your drone visits in one lap of your program.
