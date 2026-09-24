# Day 14: You're given ssds, a list of drive dicts
from functools import reduce

gbs = ____
healthy = ____
total_gb = ____
ranked = ____


def logged(func):
    ____


# 6. decorate this function with @logged
def make_label(ssd):
    return f"{ssd['serial']} | {ssd['gb']} GB"


print(make_label(ranked[0]))
