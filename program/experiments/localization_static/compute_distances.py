#!/usr/bin/python3

# For given localization data - ladder, it computes how good they were. The true and estimated distance.

import os
from sys import argv

scenario = int(argv[1])

# We are interested in these tuples
if scenario == 1:
	prefix = "localization_data/2018-05-07-at-18-10-"
	pairs = [([i, i+1], 200) for i in range(1, 7)]
	pairs += [([i, i+1], 200) for i in range(8, 14)]
	pairs += [([i, i+7], 400) for i in range(1, 8)]
elif scenario == 2:
	prefix = "localization_data/2018-05-10-at-22-04-"
	pairs = [([1, 2], 200), ([2, 3], 400), ([3, 4], 200), ([4, 1], 400)]
elif scenario == 3:
	prefix = "localization_data/2018-05-10-at-20-47-"
	pairs = [([i, i+1], 200) for i in range(1, 7)]
	pairs += [([i, i+1], 200) for i in range(8, 14)]
	pairs += [([i, i+7], 400) for i in range(1, 8)]
elif scenario == 4:
	prefix = "localization_data/2018-05-10-at-20-50-"
	pairs = [([1, 2], 200), ([2, 3], 400), ([3, 4], 200), ([4, 1], 400)]
elif scenario >= 10:
	files = os.listdir("localization_data")
	files.sort()
	prefix = 'localization_data/' + files[-1][:20]
	print(prefix)

        #prefix = "localization_data/2018-05-16-at-14-49-"
	pairs = [([i, i+1], 200) for i in range(1, 7)]
	pairs += [([i, i+1], 200) for i in range(8, 14)]
	pairs += [([i, i+7], 400) for i in range(1, 8)]
	
	pairs += [([15, 16], 200), ([15, 17], 400), ([17, 18], 200), ([18, 16], 400)]

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
