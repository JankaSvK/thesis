import threading
import logging
from collections import Set
import time
from queue import Queue
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from QueuesProvider import *
import sys

import Config
from ComplexTracker import ComplexTracker
import cv2

from GUI import GUI
from Provider import Provider

def initialize_trackers(input, output):
    trackers = []
    for cam_ind in Config.camera_indexes:
        trackers.append(ComplexTracker(cam_ind, #image_stream=Camera[cam_ind].images, tracked_points=Camera[cam_ind].tracked_points))
            input[cam_ind], output[cam_ind]))
    not_initialized_cameras = list(Config.camera_indexes)
    while not_initialized_cameras != []:
        for cam_ind in not_initialized_cameras:
            mouse_clicks = Camera[cam_ind].mouse_clicks
            if len(mouse_clicks) >= 2:
                not_initialized_cameras.remove(cam_ind)
                trackers[cam_ind].set_initial_position(mouse_clicks[-2], mouse_clicks[-1])
                trackers[cam_ind].start_tracking()


#logging.getLogger().setLevel(logging.INFO)
coords = []
for i in range(2):
    coords.append([])

provider = Provider([0, 1])
provider.initialize_cameras()
provider.start_capturing()

located_points = []
gui = GUI(coords)
guiThread = threading.Thread(target=gui.start, args=(provider.images, located_points), name="GUI")
guiThread.start()

calibration = False
trackers_initialization = True

if calibration:
    while not provider.calibrate_cameras():
        pass

    provider.calibrate_pairs()

if trackers_initialization:
    initialize_trackers(provider.images, coords)

# Getting projection matrices

firstCameraResults = provider.calibs[0].calibration_results
secondCameraResults = provider.calibs[1].calibration_results
stereoResults = provider.stereo_calibration.calibration_results

RL, RR, PL, PR, _, _, _ = cv2.stereoRectify(
    firstCameraResults.camera_matrix, firstCameraResults.distortion_coeffs,
    secondCameraResults.camera_matrix, secondCameraResults.distortion_coeffs,
    (640, 480), stereoResults.rotation_matrix, stereoResults.translation_matrix, alpha=0)

print("here")

time.sleep(1)


# # Getting points
lastAddedTime = 0
while True:
    locatedPointsHom = cv2.triangulatePoints(projMatr1=PL, projMatr2=PR, projPoints1=coords[0][-1][1], projPoints2=coords[1][-1][1]) #TODO add coordinates
    locatedPoint = [i / locatedPointsHom[3] for i in locatedPointsHom[0:3]]
    #print(locatedPoint)

    if coords[0][-1][0] - lastAddedTime > 1/10:
        located_points.append([locatedPoint[0][0], locatedPoint[1][0], locatedPoint[2][0]])
        lastAddedTime = coords[0][-1][0]