import threading
from collections import deque

import time

from CalibrationsProvider import CalibrationsProvider
from CamerasProvider import CamerasProvider
from Localization import Localization
from QueuesProvider import *
import Config
from GUI import GUI
from TrackersProvider import TrackersProvider

stop_event = threading.Event()


def run_application(options):
    if options.camera1 is not None:
        Config.camera_initialize[0] = options.camera1
    if options.camera2 is not None:
        Config.camera_initialize[1] = options.camera2

    trackers_initialization_events = [threading.Event() for _ in range(Config.objects_count * 2)]

    # Starting the cameras
    QueuesProvider.Images = [deque([], maxlen=500) for _ in range(Config.camera_count())]

    if options.video1 is None or options.video2 is None:
        videos = None
    else:
        videos = [options.video1, options.video2]

    cameras_provider = CamerasProvider(QueuesProvider.Images, stop_event, Config.camera_initialize,
                                       videos)
    cameras_provider.initialize_capturing()
    cameras_provider.start_capturing()

    # Starting GUI
    gui = GUI(stop_event=stop_event,
              objects_count=Config.objects_count,
              tracked_points=QueuesProvider.TrackedPoints2D,
              trackers_initialization_events=trackers_initialization_events,
              image_streams=QueuesProvider.Images,
              localization_data=QueuesProvider.LocalizatedPoints3D,
              console_output=QueuesProvider.ConsoleMessages)
    guiThread = threading.Thread(target=gui.start, args=(), name="GUI")
    guiThread.start()

    QueuesProvider.Threads.append(guiThread)
    QueuesProvider.Threads.append(cameras_provider.capturing_thread)

    # Calibration
    QueuesProvider.ConsoleMessages.append("Starting calibration process. Move with the chessboard in camera view.")
    calibration_provider = CalibrationsProvider(cameras_provider, stop_event, QueuesProvider.ConsoleMessages)
    # Mono camera calibration
    saved_calibration_data = [options.calibration_results1, options.calibration_results2]
    while not stop_event.is_set() and not calibration_provider.mono_calibrate(saved_calibration_data):
        pass
    # Stereo camera calibration
    while not stop_event.is_set() and not calibration_provider.stereo_calibrate(options.stereo_calibration_results):
        pass

    # Checking if it should be exited
    if stop_event.is_set():
        cameras_provider.capturing_thread.join(1)
        return
    # Tracking initialization
    trackers_provider = TrackersProvider(
        images1=QueuesProvider.Images[0], images2=QueuesProvider.Images[1],
        mouse_clicks=QueuesProvider.MouseClicks,
        coordinates=QueuesProvider.TrackedPoints2D,
        stop_event=stop_event,
        initialization_events=trackers_initialization_events,
        tracker_type=options.tracker,
        number_of_tracked_objects=Config.objects_count
    )
    trackers_provider_thread = threading.Thread(target=trackers_provider.track, name="Trackers")
    trackers_provider_thread.setDaemon(True)
    trackers_provider_thread.start()

    QueuesProvider.Threads.append(trackers_provider_thread)

    if Config.initial_bounding_boxes is not None:
        for i, tracker in enumerate(trackers_provider.trackers):
            bbox = Config.initial_bounding_boxes[tracker.camera_id][tracker.object_id]
            tracker.initialize_tracker(bbox)

    QueuesProvider.ConsoleMessages.append(
        "You can now select objects for tracking. Click on the button and click on top left corner and bottom right of the bounding box for the object.")

    # Computing matrices for localization
    Localization.compute_projection_matrices(
        calibration_provider.mono_calibration_results[0],
        calibration_provider.mono_calibration_results[1],
        calibration_provider.stereo_calibration_results
    )

    # Wait until gui fully initialized
    gui.initialized.wait()
    # Adding camera position to GUI
    stereo_results = calibration_provider.stereo_calibration_results
    camera1, camera2 = Localization.get_camera_positions(stereo_results.rotation_matrix,
                                                         stereo_results.translation_vector)
    gui.draw_cameras([camera1, camera2])


    # Endless localization
    while not stop_event.is_set():
        for i in range(Config.objects_count):
            Localization.localize_point(i)
        time.sleep(Localization.time_threshold_skip)

    # Exiting program
    Localization.save_localization_data()
