#!/usr/bin/python3

# Computes distances between the points in the ladder
# The points of the ladder has to be included
# It runs the Main.py

import os

points = [[[253, 188, 2, 2]], [[411, 304, 2, 2]]]
#points = None

# set initial bounding boxes in config
os.system("sed -i 's/initial_bounding_boxes = .*/initial_bounding_boxes = "+str(points)+"/' ../../program/Config.py")

options = " --stereo_calibration_results=data/16stereo.json" 
options += " --calibration_results1=data/16-1.json" 
options += " --calibration_results2=data/16-2.json" 
options += " --tracker=HSV"
options += " --video1=../../videos/objects/38-oval_blue_robot/1.avi"
options += " --video2=../../videos/objects/38-oval_blue_robot/2.avi"

# run the application
os.system("python3 ../../Main.py" + options)
