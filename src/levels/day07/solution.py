# Day 7: You're given scanned (a list), supplier_a and supplier_b (sets)
print(len(scanned), "scans")

unique = set(scanned)
duplicates = len(scanned) - len(unique)
print(len(unique), "different sticks,", duplicates, "double-scans")

in_both = supplier_a & supplier_b
all_models = supplier_a | supplier_b
only_a = supplier_a - supplier_b
a_sells_ddr5 = "DDR5" in supplier_a
