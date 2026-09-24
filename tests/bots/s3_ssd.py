def tend(part):
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            if get_part() == None:
                place(part)
            move(North)
        move(East)


while True:
    goto_floor(Floor.RAM)
    tend(Part.RAM)
    goto_floor(Floor.CPU)
    tend(Part.CPU)
    goto_floor(Floor.SSD)
    tend(Part.SSD)
