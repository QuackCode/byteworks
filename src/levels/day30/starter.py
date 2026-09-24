# Day 30: THE FINAL ASSEMBLY
# You're given orders, warehouse and tester
import json
from factory.cpu_tools import grade


def fetch_good(kind, is_good):
    """Keep fetching parts until is_good(part) is True. Scrap every bad one."""
    ____


def board_ok(board):
    """True if tester.install(board) works, False if it raises ValueError or KeyError."""
    ____


computers = []
for order in orders:
    cpu = fetch_good("cpu", ____)
    ram = fetch_good("ram", lambda r: r["spec"] == (32, 5600))
    ssd = fetch_good("ssd", ____)
    board = fetch_good("motherboard", board_ok)
    gpu = fetch_good("gpu", ____)
    computers.append(____)

# save computers to shipped.json

print(f"Shipped {len(computers)} computers! {warehouse}")
