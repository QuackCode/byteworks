def goto(tx, ty):
    x, y = get_pos()
    while x < tx:
        move(East)
        x += 1
    while x > tx:
        move(West)
        x -= 1
    while y < ty:
        move(North)
        y += 1
    while y > ty:
        move(South)
        y -= 1

goto_floor(Floor.GPU)
n = get_world_size()
waiting = True
while waiting:
    waiting = False
    for x in range(n):
        for y in range(n):
            goto(x, y)
            if get_part() == None:
                place(Part.GPU)
                waiting = True
            elif not can_harvest():
                waiting = True
    if waiting:
        wait(300)
swapped = True
while swapped:
    swapped = False
    for y in range(n):
        for x in range(n - 1):
            goto(x, y)
            here = measure()
            move(East)
            right = measure()
            move(West)
            if here > right:
                swap(East)
                swapped = True
    for x in range(n):
        for y in range(n - 1):
            goto(x, y)
            here = measure()
            move(North)
            up = measure()
            move(South)
            if here > up:
                swap(North)
                swapped = True
goto(0, 0)
harvest()
