def tend(part):
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if get_part() == Part.BOARD and is_faulty():
                place(Part.BOARD)
            elif can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            move(North)
        move(East)


floors = [Floor.RAM, Floor.CPU, Floor.SSD, Floor.BOARD, Floor.GPU]
while True:
    for f in floors:
        goto_floor(f)
        tend(f)
