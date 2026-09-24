# Dictionaries

A list finds items by **position**. A **dictionary** (`dict`) finds values by a **key**, like looking up a word to find its meaning:

```python
stick = {"serial": "RAM-0042", "capacity": 32, "tested": True}
print(stick["serial"], stick["capacity"], len(stick))
```

## Adding, changing, looking up safely

```python
stock = {"DDR4": 10}
stock["DDR5"] = 25        # new key: added
stock["DDR4"] += 3        # existing key: updated
print(stock)
print(stock.get("DDR9", 0))     # .get() doesn't crash if the key is missing
print("DDR4" in stock)          # checks the KEYS
```

## Removing

```python
stock = {"DDR3": 4, "DDR4": 10}
old = stock.pop("DDR3")   # removes it AND gives back the value
print(old, stock)
```

## Keys, values, items

```python
stock = {"DDR4": 10, "DDR5": 25}
print(list(stock.keys()), list(stock.values()), sum(stock.values()))
for model in stock:
    print(model, "->", stock[model])
```

## A plan for every floor

A dict can say how many laps to spend on each floor:

```py
plan = {Floor.RAM: 2, Floor.CPU: 1, Floor.SSD: 1}
while True:
    for f in plan:
        goto_floor(f)
        for lap in range(plan[f] * 9):
            if can_harvest():
                harvest()
            if get_part() == None:
                place(f)
            move(North)
            if lap % 3 == 2:
                move(East)
```

## Try this

Change the plan's numbers while watching your inventory. Which plan earns the most SSDs?
