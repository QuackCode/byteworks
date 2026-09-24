# Day 13: You're given ssds (list of dicts) and shelves (list of lists)
print(len(ssds), "drives arrived")

working = [s for s in ssds if s["health"] >= 20]
serials = [s["serial"] for s in working]
to_tb = lambda gb: gb / 1000
sizes_tb = [to_tb(s["gb"]) for s in working]
capacity = {s["serial"]: s["gb"] for s in working}
all_slots = [slot for row in shelves for slot in row]

print(len(working), "work:", serials)
