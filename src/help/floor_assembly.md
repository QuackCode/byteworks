# Final Assembly

The top floor! This is where parts from every floor become **complete computers** 🖥️.

- `goto_floor(Floor.ASSEMBLY)` takes the drone to the assembly bench
- `get_order()` gives the current customer order as a **dictionary**, like `{"RAM": 20, "GPU": 4}`
- `assemble()` uses those parts from your inventory to build **one computer**. It gives back `False` if you don't have enough
- Every finished order brings a new one, and orders get bigger over time

The goal: **build 10 computers** and bring ByteWorks back to life.

## What's missing?

```py
order = get_order()
for part in order:
    have = num_items(part)
    if have < order[part]:
        print("Need", order[part] - have, "more", part)
```

## Build as many as you can

```py
goto_floor(Floor.ASSEMBLY)
while assemble():
    print("Built a computer!")
```

`while assemble():` keeps building for as long as each `assemble()` works.

## A factory that runs itself

A great final program farms every floor, then visits Final Assembly to fill orders, forever. Put your floor code in modules, use the sorting bonus on GPUs and big merged motherboards, and watch the computers roll out.

## Try this

Make your program farm only the parts the current order is short of.
