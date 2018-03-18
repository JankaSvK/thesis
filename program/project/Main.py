import threading
import logging
from collections import Set
import time
from queue import Queue
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from Localization import Localization
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

gui = GUI(coords)
guiThread = threading.Thread(target=gui.start, args=(provider.images, QueuesProvider.LocalizatedPoints3D), name="GUI")
guiThread.start()

calibration = True
trackers_initialization = True
localization = True

if calibration:
    while not provider.calibrate_cameras():
        pass

    provider.calibrate_pairs()

if trackers_initialization:
    initialize_trackers(provider.images, coords)

if localization:
    Localization.compute_projection_matrices(
        provider.calibs[0].calibration_results,
        provider.calibs[1].calibration_results,
        provider.stereo_calibration.calibration_results
    )

time.sleep(1) #

lastAddedTime = 0
while True:
    located_point = Localization.get_3d_coordinates(coords[0][-1][1], coords[1][ -1][ 1]) # TODO: trebalo by skontrolovat ci cas sedi

    if coords[0][-1][0] - lastAddedTime > 1/10:
        QueuesProvider.LocalizatedPoints3D.append((located_point[0], located_point[1], located_point[2]))
        lastAddedTime = coords[0][-1][0]