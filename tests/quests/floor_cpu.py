goto_floor(Floor.CPU)
col = 0
while col < 3:
    row = 0
    while row < 3:
        if can_harvest():
            harvest()
        if get_part() == None:
            place(Part.CPU)
        row = row + 1
        if row < 3:
            if col % 2 == 0:
                move(North)
            else:
                move(South)
    col = col + 1
    if col < 3:
        move(East)
move(West)
move(West)
move(South)
move(South)
goto_floor(Floor.RAM)
col = 0
while col < 3:
    row = 0
    while row < 3:
        harvest()
        row = row + 1
        if row < 3:
            if col % 2 == 0:
                move(North)
            else:
                move(South)
    col = col + 1
    if col < 3:
        move(East)
move(West)
move(West)
move(South)
move(South)
