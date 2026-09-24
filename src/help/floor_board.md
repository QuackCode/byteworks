# The Motherboard Floor

Motherboards are the heart of every computer, and the trickiest part to build.

- `place(Part.BOARD)` costs **1 SSD**
- About **1 in 5** boards comes out **faulty**. You can't tell until it has finished building, when it turns red with a ⚠️
- `is_faulty()` tells you if the board under the drone is faulty
- **Harvesting a faulty board raises a `FaultyBoardError`**, which stops your whole program!
- To fix it, `place(Part.BOARD)` right on top of the faulty board. That replaces it (and costs another SSD)

## Check before you harvest

```py
goto_floor(Floor.BOARD)
while True:
    if is_faulty():
        place(Part.BOARD)
    elif can_harvest():
        harvest()
    if get_part() == None:
        place(Part.BOARD)
    move(North)
```

`elif` matters here: never harvest a board you just found was faulty.

## Big boards: merging

Here's the secret bonus. If a **square** of boards (2×2, 3×3 or bigger) is **all finished and all good**, harvesting any board in it harvests the whole square as one big board, worth **size × size × size**:

| Square | Boards in it | You get |
|---|---|---|
| 2×2 | 4 | 8 |
| 3×3 | 9 | 27 |
| 4×4 | 16 | 64 |

So the best plan is to fill the floor, fix every faulty board, **wait until the whole floor is ready**, then harvest once.

## Try this

Write a function that returns `True` only when every board on the floor is finished and good. Use it to harvest one big 3×3 board.
