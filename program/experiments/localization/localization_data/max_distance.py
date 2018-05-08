# Takes a file with localization results and computes maximum distance between any two points
# coding: utf-8

import numpy as np
from sys import argv

with open(argv[1], 'r') as f:
    data = [list(map(float, x.strip().split()))[1:] for x in f.read().strip().split('\n')]

def distance(a,b):
    na = np.array(a)
    nb = np.array(b)
    return np.linalg.norm(na - nb)

distances = [distance(a, b) for a in data for b in data]

print(max(distances))
