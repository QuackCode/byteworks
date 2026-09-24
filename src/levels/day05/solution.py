# Day 5: You're given belt, new_stick and faulty_stick
print("Belt:", belt)

# 1. add the new stick to the end
belt.append(new_stick)
# 2. remove the faulty stick
belt.remove(faulty_stick)
# 3. take the first stick off for the tester
tester = belt.pop(0)
# 4. sort the belt
belt.sort()

count = len(belt)
first_on_belt = belt[0]
last_on_belt = belt[-1]
print("Belt now:", belt)
