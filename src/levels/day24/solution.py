# Day 24: You're given scores, a list of benchmark results
import numpy as np

arr = np.array(scores)
mean = arr.mean()
median = np.median(arr)
spread = arr.std()

failures = int((arr < 5000).sum())
elite = arr[arr >= 9000]
rating = (arr - arr.min()) / (arr.max() - arr.min())

grid = arr[:12].reshape(3, 4)
row_means = grid.mean(axis=1)

print(f"{len(arr)} GPUs | mean {mean:.0f} | {failures} failed")
