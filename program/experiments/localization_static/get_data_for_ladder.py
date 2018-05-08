#!/usr/bin/python3

# Computes distances between the points in the ladder
# The points of the ladder has to be included
# It runs the Main.py

import os

# left column
leftcam_left = [[185, 83],[174, 106],[156, 133],[140, 170],[112, 216],[80, 278],[35, 366]]
rightcam_left = [[167, 98],[163, 127],[147, 161],[140, 208],[121, 267],[100, 350],[68, 458]]

# right column
leftcam_right = [[318,92],[322,116],[323,145],[326,180],[329,228],[334,293],[339,383]]
rightcam_right = [[330,105],[341,137],[354,172],[369,218],[388,277],[413,358],[455,471]]

points = [leftcam_left + leftcam_right, rightcam_left + rightcam_right]

# set initial bounding boxes in config
os.system("sed -i 's/initial_bounding_boxes = .*/initial_bounding_boxes = "+str(points)+"/' ../../program/Config.py")

options = " --stereo_calibration_results=data/16stereo.json" 
options += " --calibration_results1=data/16-1.json" 
options += " --calibration_results2=data/16-2.json" 
options += " --tracker=EXPERIMENTS"
options += " --video1=../../videos/16cm/empty1.avi"
options += " --video2=../../videos/16cm/empty2.avi"
options += " -o"+str(len(points[0]))

# run the application
os.system("python3 ../../Main.py" + options)
