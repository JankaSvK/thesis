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

stop_event = threading.Event()
provider = Provider([0, 1])


# threading.main_thread()

def initialize_trackers(input, output, trackers_stop_event):
    trackers = []
    for cam_ind in Config.camera_indexes:
        trackers.append(ComplexTracker(cam_ind,
                                       # image_stream=Camera[cam_ind].images, tracked_points=Camera[cam_ind].tracked_points))
                                       input[cam_ind], output[cam_ind]))
    not_initialized_cameras = list(Config.camera_indexes)
    while not_initialized_cameras != [] and not stop_event.is_set():
        for cam_ind in not_initialized_cameras:
            mouse_clicks = Camera[cam_ind].mouse_clicks
            if len(mouse_clicks) >= 2:
                not_initialized_cameras.remove(cam_ind)
                trackers[cam_ind].set_initial_position(mouse_clicks[-2], mouse_clicks[-1])
                trackers[cam_ind].start_tracking(trackers_stop_event)


def run_application():

    # logging.getLogger().setLevel(logging.INFO)
    coords = []
    for i in range(2):
        coords.append([])

    trackers_stop_event = threading.Event()

    provider.initialize_cameras()
    provider.start_capturing()

    gui = GUI(coords)
    guiThread = threading.Thread(target=gui.start,
                                 args=(provider.images, stop_event, QueuesProvider.LocalizatedPoints3D), name="GUI")
    guiThread.start()

    calibration = True
    trackers_initialization = True
    localization = True

    if calibration:
        while not provider.calibrate_cameras(
                use_saved=['calib_results/0/2018-03-21-at-22-12.json', 'calib_results/1/2018-03-21-at-22-12.json']):
            # while not provider.calibrate_cameras():
            pass

        provider.calibrate_pairs(use_saved='calib_results/stereo_calib_results/2018-03-21-at-22-12.json')
        # provider.calibrate_pairs() # TODO: necheckuje ci je hotovy

    if trackers_initialization:
        initialize_trackers(provider.images, coords, trackers_stop_event)

    if localization:
        Localization.compute_projection_matrices(
            provider.calibs[0].calibration_results,
            provider.calibs[1].calibration_results,
            provider.stereo_calibration.calibration_results
        )

    camera1 = [[0, 0, 0], [0, 0, 130]]
    t = provider.stereo_calibration.calibration_results.translation_matrix
    rotated_vector = provider.stereo_calibration.calibration_results.rotation_matrix.dot(np.array([[0, 0, 100]]).T) + t
    camera2 = [t.T.tolist()[0], rotated_vector.T.tolist()[0]]
    gui.draw_cameras([camera1, camera2])
    time.sleep(1)  #

    lastAddedTime = 0
    while not stop_event.is_set():
        located_point = Localization.get_3d_coordinates(coords[0][-1][1],
                                                        coords[1][-1][1])  # TODO: trebalo by skontrolovat ci cas sedi
        QueuesProvider.LocalizatedPoints3D.append(located_point)

    provider.stop_capturing()
    trackers_stop_event.set()