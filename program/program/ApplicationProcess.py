import time
import threading
from collections import deque

from .CalibrationsProvider import CalibrationsProvider
from .CalibrationsProvider import CalibrationsProvider
from .CamerasProvider import CamerasProvider
from .Localization import Localization
from .QueuesProvider import *
from . import Config
from .GUI import GUI
from .TrackersProvider import TrackersProvider


def process_options(options):
    Config.objects_count = options.objects_count
    Config.camera_initialize = [options.camera1, options.camera2]

    if options.chessboard is not None:
        try:
            chessboard = [int(x) for x in options.chessboard.split(',')]
            Config.chessboard_inner_corners = (chessboard[0], chessboard[1])
            Config.chessboard_square_size = chessboard[2]
        except Exception:
            pass

    if options.bbox is not None and options.bbox.startswith("[[[") and set(options.bbox) <= set(" [],0123456789"):
        try:
            Config.initial_bounding_boxes = eval(options.bbox)
        except:
            pass


def run_application(stop_event, options):
    process_options(options)
    trackers_initialization_events = [threading.Event() for _ in range(Config.objects_count * Config.camera_count)]
    QueuesProvider.initialize()

    # Starting the cameras
    if options.video1 is None or options.video2 is None:
        videos = None
    else:
        videos = [options.video1, options.video2]
    cameras_provider = CamerasProvider(QueuesProvider.Images, stop_event, QueuesProvider.ConsoleMessages,
                                       Config.camera_initialize, videos)
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
        time.sleep(0)

    # Stereo camera calibration
    QueuesProvider.ConsoleMessages.append(
        "Starting stereo calibration. Please move wtih a chessboard, but keep it visicble in both cameras.")
    while not stop_event.is_set() and not calibration_provider.stereo_calibrate(options.stereo_calibration_results):
        time.sleep(0)

    # Checking if it should be exited
    if stop_event.is_set():
        cameras_provider.capturing_thread.join(1)
        return

    # Wait until gui fully initialized
    gui.initialized.wait()
    time.sleep(0.5)  # We want to make sure, that first images of the video passed

    # Tracking initialization
    trackers_provider = TrackersProvider(
        images1=QueuesProvider.Images[0], images2=QueuesProvider.Images[1],
        mouse_clicks=QueuesProvider.MouseClicks,
        coordinates=QueuesProvider.TrackedPoints2D,
        stop_event=stop_event,
        console_output=QueuesProvider.ConsoleMessages,
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
            try:
                bbox = Config.initial_bounding_boxes[tracker.camera_id][tracker.object_id]
                tracker.initialize_tracker(bbox)
            except:
                print("Initialization of the tracker failed (camera={}, object={}). Continuing without it.".format(
                    tracker.camera_id + 1, tracker.object_id + 1))

    QueuesProvider.ConsoleMessages.append(
        "You can now select objects for tracking. Click on the button and click on top left corner and bottom right of the bounding box for the object.")

    # Computing matrices for localization
    Localization.compute_projection_matrices(
        calibration_provider.mono_calibration_results[0],
        calibration_provider.mono_calibration_results[1],
        calibration_provider.stereo_calibration_results
    )


    # Endless localization
    while not stop_event.is_set():
        for i in range(Config.objects_count):
            Localization.localize_point(i)
        time.sleep(0)

    # Exiting program
    Localization.save_localization_data()
