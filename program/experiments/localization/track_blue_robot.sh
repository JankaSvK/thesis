#!/bin/bash

points="[[[189, 228, 2, 2]], [[353, 367, 2, 2]]]"
sed -i "s/initial_bounding_boxes = .*/initial_bounding_boxes = $points/" ../../program/Config.py

python3 ../../Main.py \
	--stereo_calibration_results=calib_results/stereo_calib_results/38.json \
	--calibration_results1=calib_results/1/38.json \
	--calibration_results2=calib_results/2/38.json \
	-tHSV \
	--video1=videos/38/square-blue/1.avi \
	--video2=videos/38/square-blue/2.avi


