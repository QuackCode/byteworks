# Day 10: You control press (press.has_power() and press.stamp())

# 1. Countdown 3, 2, 1
for i in range(3, 0, -1):
    print(i)

good = []
dead = 0

# 2. Keep the press running while it has power
while press.has_power():
    cpu = press.stamp()
    if cpu["temp_c"] > 100:
        print("OVERHEAT! Stopping the press.")
        break
    if cpu["clock_ghz"] == 0:
        dead += 1
        continue
    good.append(cpu)

# 3. Print the serial of every good chip
for cpu in good:
    print(cpu["serial"])
