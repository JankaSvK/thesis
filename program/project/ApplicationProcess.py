import threading
import time
import numpy as np
from Localization import Localization
from OptionParser import *
from QueuesProvider import *
import Config
from ComplexTracker import ComplexTracker
from GUI import GUI
from Provider import Provider

stop_event = threading.Event()
provider = Provider([0, 1])


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


def run_application(options):
    trackers_stop_event = threading.Event()

    video_recordings = [options.video_recording1, options.video_recording2]

    provider.initialize_cameras(video_recordings)
    provider.start_capturing()

    gui = GUI(QueuesProvider.TrackedPoints2D)
    guiThread = threading.Thread(target=gui.start,
                                 args=(provider.images, stop_event, QueuesProvider.LocalizatedPoints3D), name="GUI")
    guiThread.start()

    while not stop_event.is_set() and not provider.calibrate_cameras(
            use_saved=['calib_results/0/2018-03-21-at-22-12.json', 'calib_results/1/2018-03-21-at-22-12.json']):
        # while not provider.calibrate_cameras():
        pass

    while not stop_event.is_set() and not provider.calibrate_pairs(use_saved=options.stereo_calibration_results):
        pass

    if stop_event.is_set():
        provider.stop_capturing()
        return

    initialize_trackers(provider.images, QueuesProvider.TrackedPoints2D, trackers_stop_event)

    Localization.compute_projection_matrices(
        provider.calibs[0].calibration_results,
        provider.calibs[1].calibration_results,
        provider.stereo_calibration.calibration_results
    )

    camera1, camera2 = get_camera_positions()
    gui.draw_cameras([camera1, camera2])
    time.sleep(1)  #

    while not stop_event.is_set():
        Localization.localize_point()

    # trackers.stop_tracking()
    trackers_stop_event.set()
    provider.stop_capturing()
    Localization.save_localization_data()

def get_camera_positions():
    camera1 = [[0, 0, 0], [0, 0, 130]]
    t = provider.stereo_calibration.calibration_results.translation_matrix
    rotated_vector = provider.stereo_calibration.calibration_results.rotation_matrix.dot(np.array([[0, 0, 100]]).T) + t
    camera2 = [t.T.tolist()[0], rotated_vector.T.tolist()[0]]
    return camera1, camera2