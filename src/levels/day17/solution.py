# Day 17: You're given boards (a list of dicts) and tester
installed = []
blown = []
no_bios = []
checked = 0

for board in boards:
    try:
        tester.install(board)
    except ValueError as err:
        print("Blown:", err)
        blown.append(board["serial"])
    except KeyError:
        no_bios.append(board["serial"])
    else:
        installed.append(board["serial"])
    finally:
        checked += 1


def check_volts(volts):
    if volts > 1.5:
        raise ValueError("Voltage too high")
    return True


print("Installed:", len(installed), "| Blown:", blown, "| No BIOS:", no_bios)
