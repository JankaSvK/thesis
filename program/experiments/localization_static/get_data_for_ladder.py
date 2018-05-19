#!/usr/bin/python3

# Computes distances between the points in the ladder
# The points of the ladder has to be included
# It runs the Main.py

# Only runnable on Linux based system, with `python3`
import os
from sys import argv

try:
	scenario = int(argv[1])
except:
	scenario = 1

if scenario == 1:
	# left column
	leftcam_left = [[185, 83],[174, 106],[156, 133],[140, 170],[112, 216],[80, 278],[35, 366]]
	rightcam_left = [[167, 98],[163, 127],[147, 161],[140, 208],[121, 267],[100, 350],[68, 458]]

	# right column
	leftcam_right = [[318,92],[322,116],[323,145],[326,180],[329,228],[334,293],[339,383]]
	rightcam_right = [[330,105],[341,137],[354,172],[369,218],[388,277],[413,358],[455,471]]
	
	points = [leftcam_left + leftcam_right, rightcam_left + rightcam_right]
	
	video1 = "../videos/objects/16/dots/1.avi"
	video2 = "../videos/objects/16/dots/2.avi"
elif scenario == 2:
	# table
	table_left = [[156, 17], [156, 106], [337, 33], [328, 121]]
	table_right = [[150, 16], [150, 130], [377, 33], [363, 142]]
	points = [table_left, table_right]
	video1 = "../videos/objects/16/table/1.avi"
	video2 = "../videos/objects/16/table/2.avi"
elif scenario == 3 or scenario >= 10:
	leftcam_left = [[296, 99],[270, 118],[237, 138],[199, 168],[146, 200],[82, 244],[0, 301]]
	leftcam_right = [[412, 126],[398, 147],[378, 175],[354, 208],[321, 249],[279, 304],[220, 381]]
	rightcam_left = [[155, 59],[155, 90],[146, 125],[147, 173],[138, 233],[132, 309],[124, 418]]
	rightcam_right = [[318, 66],[333, 95],[347, 132],[370, 176],[396, 232],[431, 306],[481, 411]]
	points = [leftcam_left + leftcam_right, rightcam_left + rightcam_right]
	video1 = "../videos/objects/63/dots/1.avi"
	video2 = "../videos/objects/63/dots/2.avi"
elif scenario == 4:
	table_left = [[132, 56], [130, 157], [331, 103], [315, 207]]
	table_right = [[133, 53], [135, 194], [426, 64], [404, 196]]
	points = [table_left, table_right]
	video1 = "../videos/objects/63/table/1.avi"
	video2 = "../videos/objects/63/table/2.avi"

# Calibration results
if scenario == 1 or scenario == 2:
	stereo = "data/16stereo.json"
	cal1 = "data/16-1.json"
	cal2 = "data/16-2.json"
elif scenario >= 10:
	mod = scenario % 10
	stereo = "data/63stereo-{}.json".format(mod)
	cal1 = "data/63-1-{}.json".format(mod)
	cal2 = "data/63-2-{}.json".format(mod)
else:
	stereo = "data/63stereo.json"
	cal1 = "data/63-1.json"
	cal2 = "data/63-2.json"

# set initial bounding boxes in config
os.system("sed -i 's/initial_bounding_boxes = .*/initial_bounding_boxes = "+str(points)+"/' ../../program/Config.py")

options = " --stereo_calibration_results="+stereo 
options += " --calibration_results1="+cal1 
options += " --calibration_results2="+cal2 
options += " --tracker=EXPERIMENTS"
options += " --video1="+video1
options += " --video2="+video2
options += " -o"+str(len(points[0]))

# run the application
os.system("python3 ../../Main.py" + options)
