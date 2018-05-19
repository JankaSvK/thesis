#!/usr/bin/python3 

from context import program
from sys import argv
from trackers_experiments_helper import run_trackers_experiment

try:
    experiment_id = int(argv[1])
except Exception:
    experiment_id = 1

try:
    tracker_id = int(argv[2])
    if tracker_id < 0 or tracker_id > 9:
        tracker_id = 0
except Exception:
    tracker_id = 0


gui_on = True
prefix = 'material/'
video = None
empty = None
bbox = None
hsv_bbox = None
trackers = ['KCF']
all_trackers = ['SIMPLEBACKGROUND', 'MIL', 'BOOSTING', 'TLD', 'MEDIANFLOW', 'HSV', 'PATTERNMATCHING', 'CORRELATION', 'MOSSE']

if experiment_id == 1:
    # Testing performance of all trackers
    video = prefix + 'robot.avi'
    empty = prefix  + 'empty.jpg'
    hsv_bbox = (345, 226, 7, 28)
    bbox = (239, 202, 147, 139)
    trackers = all_trackers

elif experiment_id == 2:
    # with the orange cap on the robot
    video = prefix + 'robot2.avi'
    empty = prefix + 'empty2.jpg'
    hsv_bbox = (243, 232, 54, 36) # only orange color
    bbox = (193, 188, 168, 165)
    trackers = all_trackers

elif experiment_id == 3:
    # Experiment to test occlusion
    video = prefix + 'robot-occlusion.avi'
    empty = prefix + 'empty-occlusion.jpg'
    bbox = (354, 47, 121, 98)
    trackers = [all_trackers[tracker_id]]

elif experiment_id == 4:
    # Multiple objects tracking
    video = prefix + 'two-objects.avi'
    empty = None
    bbox = [(369, 192, 127, 136), (147, 217, 96, 111)]
    tracker = all_trackers[tracker_id]
    trackers = [tracker, tracker]

elif experiment_id == 5:
    # Multiple objects tracking for HSV tracker
    video = prefix + 'two-colors.avi'
    empty = None
    bbox = [(410, 226, 92, 101), (156, 245, 81, 79)]
    trackers = ['HSV', 'HSV']

elif experiment_id == 6:
    # Experiment to test occlusion
    video = prefix + 'robot-occlusion.avi'
    empty = prefix + 'empty-occlusion.jpg'
    hsv_bbox = (345, 226, 7, 28)
    bbox = (369, 40, 101, 104)
    trackers = all_trackers

elif experiment_id == 7:
    # Experiment with partial occlusion
    video = prefix + '1.mp4'
    empty = prefix + '1.jpg'
    bbox = (420, 179, 183, 175) #(417, 169, 187, 179)
    hsv_bbox = (460, 215, 48, 22)
    tracker_id = 0
    all_trackers.remove('HSV')
    trackers = ['HSV'] + all_trackers

elif experiment_id == 8:
    # Experiment with full occlusion -- tunnel
    video = prefix + '3.mp4'
    empty = prefix + '3.jpg'
    bbox = (356, 177, 153, 135) #(417, 169, 187, 179)
    hsv_bbox = (393, 201, 33, 18)
    tracker_id = 0
    all_trackers.remove('HSV')
    #trackers = ['HSV'] + all_trackers
    trackers = ['HSV', 'MEDIANFLOW']

run_trackers_experiment(gui_on, trackers, empty, bbox, video, hsvbbox=hsv_bbox)

