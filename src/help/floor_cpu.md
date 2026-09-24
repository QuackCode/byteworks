# The CPU Floor

The lift is working! The CPU floor starts **empty**. You build chips yourself, and they need time to bake.

## Riding the lift

```py
goto_floor(Floor.CPU)
print(get_floor())
goto_floor(Floor.RAM)
```

The lift takes 400 ticks, so don't ride it more than you need to. The ▲ ▼ buttons only move the **camera**. Tick **Follow drone** to keep the camera on the drone.

## Building chips

- `place(Part.CPU)` starts baking a chip on an **empty** tile (CPUs cost nothing to place)
- A green bar shows the chip baking
- When it's ready, `harvest()` gives you CPUs

⚠️ **Harvesting a chip before it's ready destroys it!** Always check with `can_harvest()` first.

## A CPU farming loop

```py
goto_floor(Floor.CPU)
row = 0
while True:
    if can_harvest():
        harvest()
    if get_part() == None:
        place(Part.CPU)
    if row < 2:
        move(North)
        row = row + 1
    else:
        move(South)
        move(South)
        row = 0
```

`None` is Python's value for "nothing here".

## 🎯 Quest

**Farm both floors in one program: harvest 5 RAM and 5 CPUs in a single run.** Doing it lets you buy **For Loops & range** (you'll still need its parts).

Do a lap of the CPU floor (harvest what's ready, `place` on empty tiles), `goto_floor(Floor.RAM)`, do a lap there, and loop. Chips need time to bake, so the CPUs come in on the second time round.
