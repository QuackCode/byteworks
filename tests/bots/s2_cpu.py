while True:
    goto_floor(Floor.CPU)
    i = 0
    while i < 9:
        if can_harvest():
            harvest()
        if get_part() == None:
            place(Part.CPU)
        move(North)
        i = i + 1
        if i % 3 == 0:
            move(East)
    goto_floor(Floor.RAM)
    i = 0
    while i < 9:
        harvest()
        move(North)
        i = i + 1
        if i % 3 == 0:
            move(East)
