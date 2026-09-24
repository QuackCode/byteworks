# Day 30: THE FINAL ASSEMBLY
# You're given orders, warehouse and tester
import json
from factory.cpu_tools import grade


def fetch_good(kind, is_good):
    """Keep fetching parts until is_good(part) is True. Scrap every bad one."""
    while True:
        part = warehouse.fetch(kind)
        if is_good(part):
            return part
        warehouse.scrap(part)


def board_ok(board):
    """True if tester.install(board) works, False if it raises ValueError or KeyError."""
    try:
        tester.install(board)
        return True
    except (ValueError, KeyError):
        return False


computers = []
for order in orders:
    gaming = order["type"] == "GAMING"
    min_score = 8000 if gaming else 5000
    cpu = fetch_good("cpu", lambda c: grade(c) == "GAMING" if gaming else grade(c) != "REJECT")
    ram = fetch_good("ram", lambda r: r["spec"] == (32, 5600))
    ssd = fetch_good("ssd", lambda s: s["health"] >= 20)
    board = fetch_good("motherboard", board_ok)
    gpu = fetch_good("gpu", lambda g: g["score"] >= min_score)
    computers.append({
        "order": order["id"],
        "cpu": cpu["serial"],
        "ram": ram["serial"],
        "ssd": ssd["serial"],
        "motherboard": board["serial"],
        "gpu": gpu["serial"],
    })

# save computers to shipped.json
with open("shipped.json", "w") as f:
    json.dump(computers, f)

print(f"Shipped {len(computers)} computers! {warehouse}")
