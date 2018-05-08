#!/usr/bin/python3

# For given localization data - ladder, it computes how good they were. The true and estimated distance.

import os

prefix = "localization_data/2018-05-07-at-18-10-"

# We are interested in these tuples
points_in_column = 7
pairs = [([i, i+1], 200) for i in range(1, 7)]
pairs += [([i, i+1], 200) for i in range(8, 14)]

pairs += [([i, i+7], 400) for i in range(1, 8)]

os.system("rm .results.txt")
for pair, dist in pairs:
	files = [prefix + str(i) + ".txt" for i in pair]
	os.system("cat {0} {1} > .tmp.txt".format(files[0], files[1]))
	os.system("python3 max_distance.py .tmp.txt >> .results.txt")

with open(".results.txt", "r") as f:
	lines = list(map(float, f.read().strip().split('\n')))

for i, (pair, dist) in enumerate(pairs):
	percentage = (lines[i] - dist) / dist * 100
	print("{2} & {3} & {0} & {1:.2f} & {4:.2f} \% \\\\".format(dist, lines[i], pair[0], pair[1], percentage))
