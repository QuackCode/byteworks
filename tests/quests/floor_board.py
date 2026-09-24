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

goto_floor(Floor.BOARD)
square = [(0, 0), (0, 1), (1, 1), (1, 0)]
while True:
    ready = 0
    for spot in square:
        goto(spot[0], spot[1])
        if get_part() == None or is_faulty():
            place(Part.BOARD)
        elif can_harvest():
            ready += 1
    if ready == 4:
        goto(0, 0)
        harvest()
        break
    wait(300)
