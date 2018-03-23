import threading
import logging
from collections import Set
import time
from queue import Queue
import matplotlib.pyplot as plt
import numpy as np
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
    while not provider.calibrate_cameras(use_saved=['calib_results/0/2018-03-21-at-22-12.json', 'calib_results/1/2018-03-21-at-22-12.json']):
    # while not provider.calibrate_cameras():
        pass

    provider.calibrate_pairs(use_saved='calib_results/stereo_calib_results/2018-03-21-at-22-12.json')
    provider.calibrate_pairs() # TODO: necheckuje ci je hotovy



if trackers_initialization:
    initialize_trackers(provider.images, coords)

if localization:
    Localization.compute_projection_matrices(
        provider.calibs[0].calibration_results,
        provider.calibs[1].calibration_results,
        provider.stereo_calibration.calibration_results
    )


start1 = {'x':0, 'y':0, 'z':0}
end1   = {'x':0, 'y':0, 'z':100}
camera1 = { 'start':start1, 'end':end1 }

t = provider.stereo_calibration.calibration_results.translation_matrix
start2 = {'x':t[0][0], 'y':t[1][0], 'z':t[2][0]} # + translation vector
end2   = {'x':t[0][0], 'y':t[1][0], 'z':t[2][0] + 100}

tmp = np.array([[0, 0, 100]]).T
res = provider.stereo_calibration.calibration_results.rotation_matrix.dot(tmp)
end2 = {'x': t[0][0]+res[0][0], 'y':t[1][0]+res[1][0], 'z':t[2][0]+res[2][0]}
camera2 = { 'start':start2, 'end':end2 }

gui.draw_cameras([camera1, camera2])

time.sleep(1) #

lastAddedTime = 0
while True:
    located_point = Localization.get_3d_coordinates(coords[0][-1][1], coords[1][ -1][ 1]) # TODO: trebalo by skontrolovat ci cas sedi

    if coords[0][-1][0] - lastAddedTime > 1/10:
        QueuesProvider.LocalizatedPoints3D.append((located_point[0], located_point[1], located_point[2]))
        lastAddedTime = coords[0][-1][0]
        #print(located_point)