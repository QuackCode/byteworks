# Day 11: Build reusable functions for the CPU floor

def build_cpu(cores, clock_ghz=3.0):
    return {"cores": cores, "clock_ghz": clock_ghz, "score": cores * clock_ghz}


def is_faulty(cpu):
    return cpu["clock_ghz"] == 0 or cpu["temp_c"] > 100


def total_cores(*cpus):
    total = 0
    for cpu in cpus:
        total += cpu["cores"]
    return total


# Try them out!
fast = build_cpu(8, 4.5)
print(fast)
