# Day 12: You're given batch, a list of CPU dicts
# 1. your imports go here
import math
import random
import statistics as stats
from factory.cpu_tools import grade

boxes = math.ceil(len(batch) / 12)
audit = random.choice(batch)

clocks = []
for cpu in batch:
    clocks.append(cpu["clock_ghz"])
avg_clock = stats.mean(clocks)

grades = []
for cpu in batch:
    grades.append(grade(cpu))

print("Boxes:", boxes, "| Average clock:", avg_clock)
print(grades)
