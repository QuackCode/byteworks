def home():
    x, y = get_pos()
    for i in range(x):
        move(West)
    for i in range(y):
        move(South)

def work(part):
    if can_harvest():
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
for f in [Floor.RAM, Floor.CPU, Floor.SSD]:
    goto_floor(f)
    tend(f)
