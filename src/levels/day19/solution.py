# Day 19: Your folder has orders.txt, specs.json and boards.csv
import csv
import json
import os

# 1. read orders.txt into a list of lines
with open("orders.txt") as f:
    orders = f.read().splitlines()

# 2. read specs.json
with open("specs.json") as f:
    specs = json.load(f)
socket = specs["socket"]

# 3 & 4. read boards.csv
with open("boards.csv") as f:
    rows = list(csv.DictReader(f))
passed = [row["serial"] for row in rows if row["status"] == "PASS"]

# 5. write production.log
with open("production.log", "w") as f:
    for order in orders:
        f.write(f"BUILT {order}\n")

# 6. append SHIFT END
with open("production.log", "a") as f:
    f.write("SHIFT END\n")

log_exists = os.path.exists("production.log")
print(len(orders), "orders logged. Socket:", socket, "| Passed:", passed)
