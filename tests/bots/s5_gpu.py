def home():
    x, y = get_pos()
    for i in range(x):
        move(West)
    for i in range(y):
        move(South)

def work(part):
    if get_part() == Part.BOARD and is_faulty():
        place(Part.BOARD)
    elif can_harvest():
        harvest()
    if get_part() == None:
        place(part)

def tend(part):
    n = get_world_size()
    for col in range(n):
        for row in range(n - 1):
            work(part)
            if col % 2 == 0:
                move(North)
            else:
                move(South)
        work(part)
        if col < n - 1:
            move(East)
    for i in range(n - 1):
        move(West)
    if n % 2 == 1:
        for i in range(n - 1):
            move(South)


home()
floors = [Floor.RAM, Floor.CPU, Floor.SSD, Floor.BOARD, Floor.GPU]
while True:
    for f in floors:
        goto_floor(f)
        tend(f)
