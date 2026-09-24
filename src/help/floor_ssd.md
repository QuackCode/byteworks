# The SSD Floor

SSDs are built from other parts. Each `place(Part.SSD)` costs **1 RAM and 1 CPU**, but a finished SSD gives you **2**. Check the costs in the **Upgrades** tree if prices change.

If you can't afford it, `place()` just gives back `False` and nothing happens.

## Planning with `num_items`

Your drone has to keep three floors busy now. Check you have the parts before you place:

```py
def can_build_ssd():
    return num_items(Part.RAM) >= 1 and num_items(Part.CPU) >= 1

goto_floor(Floor.SSD)
row = 0
while True:
    if can_harvest():
        harvest()
    if get_part() == None and can_build_ssd():
        place(Part.SSD)
    if row < 2:
        move(North)
        row = row + 1
    else:
        move(South)
        move(South)
        row = 0
```

## Keeping every floor busy

Placing SSDs uses up RAM and CPUs, so if you only farm SSDs you'll run out. A good program visits **all three floors** in turn.

Tip: a bigger RAM grid (in Upgrades) means more RAM every lap.

## 🎯 Quest

**Harvest 10 SSDs in one run.** Doing it lets you buy **Lists** (you'll still need its parts).

SSDs cost RAM and CPUs, so keep all three floors busy in one program.
