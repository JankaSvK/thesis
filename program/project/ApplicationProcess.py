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
from Tracking import Tracking

stop_event = threading.Event()
provider = Provider()

def run_application(options):
    if options.camera1 is not None:
        Config.camera_initialize[0] = options.camera1
    if options.camera2 is not None:
        Config.camera_initialize[1] = options.camera2

    # Starting the cameras
    provider.initialize_cameras(Config.camera_initialize, [options.video_recording1, options.video_recording2])
    provider.start_capturing()

    # Starting GUI
    gui = GUI(QueuesProvider.TrackedPoints2D)
    guiThread = threading.Thread(target=gui.start,
                                 args=(provider.images, stop_event, QueuesProvider.LocalizatedPoints3D), name="GUI")
    guiThread.start()

    # Mono camera calibration
    while not stop_event.is_set() and not provider.calibrate_cameras(
            use_saved=[options.calibration_results1, options.calibration_results2]):
        pass

    # Stereo camera calibration
    while not stop_event.is_set() and not provider.calibrate_pairs(use_saved=options.stereo_calibration_results):
        pass

    # Checking if it should be exited
    if stop_event.is_set():
        provider.stop_capturing()
        return

    # Tracking initialization
    QueuesProvider.Images = provider.images #TODO: fix
    tracking = Tracking(tracker_type=options.tracker, stop_event=stop_event)
    Tracking.tracking_object = tracking
    tracking.wait_until_all_trackers_initialized()

    # Computing matrices for localization
    Localization.compute_projection_matrices(
        provider.calibs[0].calibration_results,
        provider.calibs[1].calibration_results,
        provider.stereo_calibration.calibration_results
    )

    # Adding camera position to GUI
    camera1, camera2 = get_camera_positions()
    gui.draw_cameras([camera1, camera2])

    time.sleep(1)

    # Endless localization
    while not stop_event.is_set():
        Localization.localize_point()

    # Exiting program
    provider.stop_capturing()
    Localization.save_localization_data()

def get_camera_positions():
    camera1 = [[0, 0, 0], [0, 0, 130]]
    t = provider.stereo_calibration.calibration_results.translation_matrix
    rotated_vector = provider.stereo_calibration.calibration_results.rotation_matrix.dot(np.array([[0, 0, 100]]).T) + t
    camera2 = [t.T.tolist()[0], rotated_vector.T.tolist()[0]]
    return camera1, camera2