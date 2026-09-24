# Day 21: Design the motherboard blueprints

class Motherboard:
    def __init__(self, serial, socket, ram_slots=4):
        ____

    def install_ram(self, stick):
        ____

    def __str__(self):
        ____


class GamingBoard(____):
    def __init__(self, serial, socket):
        ____


board = Motherboard("MB-0042", "AM5")
board.install_ram("DDR5-32GB")
print(board, board.ram)
