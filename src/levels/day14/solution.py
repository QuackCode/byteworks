# Day 14: You're given ssds, a list of drive dicts
from functools import reduce

gbs = list(map(lambda s: s["gb"], ssds))
healthy = list(filter(lambda s: s["health"] >= 20, ssds))
total_gb = reduce(lambda a, b: a + b, gbs)
ranked = sorted(ssds, key=lambda s: s["health"], reverse=True)


def logged(func):
    def wrapper(*args):
        print("Running", func.__name__)
        return func(*args)
    return wrapper


# 6. decorate this function with @logged
@logged
def make_label(ssd):
    return f"{ssd['serial']} | {ssd['gb']} GB"


print(make_label(ranked[0]))
