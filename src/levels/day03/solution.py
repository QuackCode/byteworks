# Day 3: The calculator terminal gives you:
# parts_per_hour, hours, cost_per_part, budget, is_powered
print("Today:", parts_per_hour, "parts/hour for", hours, "hours")

total_parts = parts_per_hour * hours
total_cost = total_parts * cost_per_part
boxes = total_parts // 12       # full boxes of 12
leftover = total_parts % 12     # parts that don't fill a box
over_budget = total_cost > budget
can_run = is_powered and not over_budget
