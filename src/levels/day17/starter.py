# Day 17: You're given boards (a list of dicts) and tester
installed = []
blown = []
no_bios = []
checked = 0

for board in boards:
    tester.install(board)          # 💥 crashes on faulty boards! Wrap it in try/except
    installed.append(board["serial"])


def check_volts(volts):
    ____


print("Installed:", len(installed), "| Blown:", blown, "| No BIOS:", no_bios)
