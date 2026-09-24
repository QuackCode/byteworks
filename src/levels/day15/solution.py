# Day 15: This report crashes! Fix each bug (they're all different error types).
ssds = [
    {"serial": "SSD-01", "gb": 512, "health": 91},
    {"serial": "SSD-02", "gb": 1000, "health": 45},
    {"serial": "SSD-03", "gb": 2000, "health": 77},
    {"serial": "SSD-04", "gb": 2000, "health": 30},
]
drive_count = len(ssds)
print("Drives: " + str(drive_count))

last = ssds[drive_count - 1]
print("Last drive:", last["serial"])

total = 0
for s in ssds:
    total += s["gb"]
print("Total GB:", total)

capacity = int("2000")
print("Warehouse capacity:", capacity)

ssds.append({"serial": "SSD-05", "gb": 256, "health": 100})
print("Drives after restock:", len(ssds))
