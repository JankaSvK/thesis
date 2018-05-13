#!/usr/bin/python3
import os
from sys import argv

if os.name == 'nt':
	python = "python"
else:
	python = "python3"

try:
    experiment_id = int(argv[1])
except:
    experiment_id = 38

try:
    objects_id = int(argv[2])
except:
    objects_id = 1


def command(video1, video2, calib1, calib2, stereo, bbox = None, tracker = None, objects = 1):
    return '{} ../../Main.py --video1={} --video2={} --calibration_results1={} --calibration_results2={} ' \
           '--stereo_calibration_results={} --bbox={} -t{} -o{}'.format(python, video1, video2, calib1, calib2,
                                                                              stereo, bbox, tracker, objects)

bbox = None
tracker = None
objects = 1
obj_videos = "../videos/objects/"
if experiment_id == 38:
    data = "38.json"

    if objects_id == 1:
        bbox = "[[[189,228,2,2]],[[353,367,2,2]]]"
        video1 = obj_videos + "38/square_blue/1.avi"
        video2 = obj_videos + "38/square_blue/2.avi"
        tracker = "HSV"
    else:
        bbox = "[[[230,224,25,23]],[[404,349,33,31]]]"
        video1 = obj_videos + "38/oval/1.avi"
        video2 = obj_videos + "38/oval/2.avi"
        tracker = "HSV"

elif experiment_id == 16:
    data = "16.json"

    if objects_id == 1:
        bbox = "[[[189,228,2,2]],[[353,367,2,2]]]"
        video1 = obj_videos + "16/shampoo/1-c.avi"
        video2 = obj_videos + "16/shampoo/2-c.avi"
    elif objects_id == 2:
        bbox = "[[[189,228,2,2]],[[353,367,2,2]]]"
        video1 = obj_videos + "16/shampoo/1.avi"
        video2 = obj_videos + "16/shampoo/2.avi"

    tracker = "SIMPLEBACKGROUND"

elif experiment_id == 43:
    data = "43.json"

    if objects_id == 1:
        bbox = "[[[110,110,59,95]],[[260,4,68,101]]]"
        video1 = obj_videos + "43/milk/1.avi"
        video2 = obj_videos + "43/milk/2.avi"
    else:
        bbox = "[[[107,116,74,82],[336,141,56,95]],[[261,4,67,112],[425,158,82,112]]]"
        video1 = obj_videos + "43/milk_popcorn/1.avi"
        video2 = obj_videos + "43/milk_popcorn/2.avi"
        objects = 2
    tracker = "CORRELATION"
else:
    print("Not recognized set of videos")
    exit(0)


calib1 = "calib_results/1/" + data
calib2 = "calib_results/2/" + data
stereo = "calib_results/stereo_calib_results/" + data

cmd = command(video1, video2, calib1, calib2, stereo, bbox, tracker, objects)
print("Calling application with following parameters...")
print(cmd)
print()
os.system(cmd)
