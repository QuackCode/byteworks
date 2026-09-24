# Day 8: You're given inventory (a dict), delivery (a number) and order (a dict)
print("Stock:", inventory)
print("Order:", order)

inventory["DDR5"] += delivery         # 1. add the delivery to DDR5
inventory["LPDDR5"] = 20              # 2. add LPDDR5 with 20 in stock
retired = inventory.pop("DDR3")
inventory[order["model"]] -= order["qty"]   # 4. fill the order

total_sticks = sum(inventory.values())
models = list(inventory.keys())
print("Stock now:", inventory)
