import threading
import logging
from collections import Set
import time
from queue import Queue
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import sys

from ComplexTracker import ComplexTracker
import cv2

from GUI import GUI
from Provider import Provider

def clickCounter(queue, number_of_cameras, image_streams, output_streams):
    bboxes = []
    trackers = []

    for i in range(number_of_cameras):
        bboxes.append([])
        trackers.append(ComplexTracker(i,image_stream=image_streams[i], output_stream=output_streams[i]))

    bboxes_created = set()

    while len(bboxes_created) != number_of_cameras:
        (id, x, y) = queue.get()
        if len(bboxes[id]) < 2:
            bboxes[id].append((x, y))
        if len(bboxes[id]) == 2:
            bboxes_created.add(id)
            trackers[id].set_initial_position(bboxes[id][0], bboxes[id][1])
            trackers[id].start_tracking()

            # start tracking
    print("Got all bounding box")

    return (bboxes, trackers)
#logging.getLogger().setLevel(logging.INFO)
coords = []
for i in range(2):
    coords.append([])

provider = Provider([0, 1])
provider.initialize_cameras()
provider.start_capturing()

gui_actions_queue = Queue()
located_points = []
gui = GUI(gui_actions_queue, coords)
guiThread = threading.Thread(target=gui.start, args=(provider.images, located_points), name="GUI")
guiThread.start()

while not provider.calibrate_cameras():
    #print("New calibration")
    pass

print("!!! Cameras calibrated")


provider.calibrate_pairs()

#### One small step further

bboxes = clickCounter(gui_actions_queue, 2, provider.images, coords)

print("Got here")

#while True:
#    print(coords[0][-1][0] - provider.images[0][-1][0])
#Draw them



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