# Day 21: Design the motherboard blueprints

class Motherboard:
    def __init__(self, serial, socket, ram_slots=4):
        self.serial = serial
        self.socket = socket
        self.ram_slots = ram_slots
        self.ram = []

    def install_ram(self, stick):
        if len(self.ram) >= self.ram_slots:
            raise ValueError("No free RAM slots")
        self.ram.append(stick)

    def __str__(self):
        return f"Motherboard {self.serial} ({self.socket})"


class GamingBoard(Motherboard):
    def __init__(self, serial, socket):
        super().__init__(serial, socket, ram_slots=8)
        self.rgb = True


board = Motherboard("MB-0042", "AM5")
board.install_ram("DDR5-32GB")
print(board, board.ram)
