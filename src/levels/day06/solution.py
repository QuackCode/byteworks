# Day 6: You're given specs, a list of (capacity, speed) tuples
print("Batch:", specs)

STANDARD = (32, 5600)
capacity, speed = STANDARD

matching = specs.count(STANDARD)
first_match = specs.index(STANDARD)
print(matching, "sticks match the standard")

fast_spec = (capacity, 6400)
