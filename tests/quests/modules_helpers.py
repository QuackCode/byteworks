def lap():
    n = get_world_size()
    for col in range(n):
        for row in range(n):
            harvest()
            if row < n - 1:
                if col % 2 == 0:
                    move(North)
                else:
                    move(South)
        if col < n - 1:
            move(East)
    x, y = get_pos()
    for i in range(x):
        move(West)
    for i in range(y):
        move(South)
