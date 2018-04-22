import threading
import numpy as np
from Localization import Localization
from QueuesProvider import *
import Config
from GUI import GUI
from Provider import Provider
from TrackersProvider import TrackersProvider

stop_event = threading.Event()
provider = Provider()

def run_application(options):
    if options.camera1 is not None:
        Config.camera_initialize[0] = options.camera1
    if options.camera2 is not None:
        Config.camera_initialize[1] = options.camera2


    trackers_initialization_events = [threading.Event() for _ in range(Config.objects_count * 2)]

    # Starting the cameras
    provider.initialize_cameras(Config.camera_initialize, [options.video_recording1, options.video_recording2])
    provider.start_capturing(stop_event)

    QueuesProvider.Images = provider.images

    # Starting GUI
    gui = GUI(QueuesProvider.TrackedPoints2D)
    guiThread = threading.Thread(target=gui.start,
                                 args=(provider.images, stop_event, trackers_initialization_events, QueuesProvider.LocalizatedPoints3D), name="GUI")
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
    trackers_provider = TrackersProvider(
        images1 = provider.images[0], images2 = provider.images[1],
        mouse_clicks = QueuesProvider.MouseClicks,
        coordinates = QueuesProvider.TrackedPoints2D,
        stop_event = stop_event,
        initialization_events = trackers_initialization_events,
        tracker_type = options.tracker,
        number_of_tracked_objects = Config.objects_count
    )
    trackers_provider_thread = threading.Thread(target=trackers_provider.track, name="Trackers")
    trackers_provider_thread.start()

    # Computing matrices for localization
    Localization.compute_projection_matrices(
        provider.calibs[0].calibration_results,
        provider.calibs[1].calibration_results,
        provider.stereo_calibration.calibration_results
    )

    # Wait until gui fully initialized
    gui.initialized.wait()

    # Adding camera position to GUI
    camera1, camera2 = get_camera_positions()
    gui.draw_cameras([camera1, camera2])

    # Endless localization
    while not stop_event.is_set():
        for i in range(Config.objects_count):
            Localization.localize_point(i)

    # Exiting program
    provider.stop_capturing()
    Localization.save_localization_data()

def get_camera_positions():
    length = 250
    camera1 = [[0, 0, 0], [0, 0, length]]
    t = provider.stereo_calibration.calibration_results.translation_matrix
    rotated_vector = provider.stereo_calibration.calibration_results.rotation_matrix.dot(np.array([[0, 0, length]]).T) + t
    camera2 = [t.T.tolist()[0], rotated_vector.T.tolist()[0]]
    return camera1, camera2



#### TODO
### soknci sa video, vypni sa
### uchadzajuci cas vo videach