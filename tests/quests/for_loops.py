for lap in range(2):
    for col in range(3):
        for row in range(3):
            harvest()
            if row < 2:
                if col % 2 == 0:
                    move(North)
                else:
                    move(South)
        if col < 2:
            move(East)
    move(West)
    move(West)
    move(South)
    move(South)
