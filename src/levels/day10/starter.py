# Day 10: You control press (press.has_power() and press.stamp())

# 1. Countdown 3, 2, 1
for i in ____:
    print(i)

good = []
dead = 0

# 2. Keep the press running while it has power
while ____:
    cpu = press.stamp()
    # stop the press if the chip is over 100°C
    # skip dead chips (clock_ghz == 0) and count them
    good.append(cpu)

# 3. Print the serial of every good chip
