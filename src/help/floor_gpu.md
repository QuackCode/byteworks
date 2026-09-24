# The GPU Floor

Graphics chips are graded. Every GPU gets a **benchmark score from 0 to 9**, shown in the corner of its tile.

- `place(Part.GPU)` costs **1 motherboard and 1 CPU**
- `measure()` gives the score of the chip under the drone
- `swap(direction)` swaps this chip with its neighbour (`North`, `East`, `South` or `West`). It doesn't wrap round: at the edge it gives back `False`

## The sorting bonus 🎯

Harvesting an ordinary GPU gives you **1**. But if, at the moment you harvest, the **whole floor is sorted**:
- every row gets bigger (or stays the same) going **East**, and
- every column gets bigger (or stays the same) going **North**

...then the whole floor is harvested at once, and **every chip is worth size × size**. On a 3×3 floor that's 9 chips × 9 = **81 GPUs** instead of 1!

## Bubble sort, in words

To sort a row, walk along it comparing each chip with the one to its East. If the left one is bigger, swap them. After one walk, the biggest chip has "bubbled" to the end. Walk again and again until nothing needs swapping. Then do the same for the columns.

## One pass along a row

```py
for i in range(2):
    here = measure()
    move(East)
    right = measure()
    move(West)
    if here > right:
        swap(East)
    move(East)
```

Start at the West end of the row. On a bigger floor, go round `size - 1` times instead of 2.

## Try this

Sort a whole 3×3 GPU floor and harvest it for the big bonus. Hint: rows first, then columns, and keep going until a full pass makes no swaps.
