import threading as t
import time

import cv2

from . import Config
from .QueuesEntries import ImageEntry


class MissingVideoSources(RuntimeError):
    pass


class CamerasProvider(object):
    def __init__(self, images_queues, stop_event, console_output, camera_indices=None, video_recordings=None):
        self.camera_indices = camera_indices
        self.video_recordings = video_recordings
        self.image_entries = images_queues
        self.console_output = console_output
        self.stop_event = stop_event
        self.input_end = t.Event()

        self.captures = []
        self.fps = [None, None]
        self.capturing_thread = None
        self.width = Config.image_width
        self.height = Config.image_height
        self.thread_start = None

        if video_recordings is None and camera_indices is None:
            raise MissingVideoSources

    def initialize_capturing(self):
        sources = self.video_recordings or self.camera_indices
        if len(sources) != Config.camera_count:
            raise MissingVideoSources
        try:
            self.captures = [cv2.VideoCapture(s) for s in sources]
        except:
            raise MissingVideoSources
        self.setup_cameras()

    def setup_cameras(self):
        for cam_ind, capture in enumerate(self.captures):
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            self.fps[cam_ind] = capture.get(cv2.CAP_PROP_FPS)

            # capture.set(cv2.CAP_PROP_SETTINGS, 1) # open properties window for camera configuration

    def start_capturing(self):
        target = self.capture_live if self.video_recordings is None else self.capture_from_videos

        self.capturing_thread = t.Thread(target=target, args=(), name="VideoCapture")
        self.capturing_thread.setDaemon(True)
        self.thread_start = time.time()

        self.capturing_thread.start()

    def stop_capturing(self):
        for i, capture in enumerate(self.captures):
            capture.release()
            print("Camera {} released.".format(i))

    def capture_live(self):
        while not self.stop_event.is_set():
            for i, capture in enumerate(self.captures):
                self.capture_and_save_image(i)
        self.stop_capturing()

    def capture_from_videos(self):
        self.processed_images = [0, 0]
        while not self.stop_event.is_set():
            times = [self.processed_images[i] / (self.fps[i] or 30) for i in range(Config.camera_count)]
            shorter = times[0] > times[1]  # get index of minimum

            time_to_sleep = times[shorter] - (time.time() - self.thread_start)
            if time_to_sleep > 0.01:
                time.sleep(time_to_sleep)  # to not have faster videos than reality

            self.processed_images[shorter] += 1
            ok = self.capture_and_save_image(shorter)
            if not ok:
                self.console_output.append("Video ended. The views will not be updated.")
                self.input_end.set()
                break
        self.stop_capturing()

    def capture_and_save_image(self, cam_index):
        ok, frame = self.captures[cam_index].read()
        if not ok:
            return False

        frame = cv2.resize(frame, (self.width, self.height))
        image_entry = ImageEntry(frame)

        if self.stop_event.is_set():
            return False
        self.image_entries[cam_index].append(image_entry)
        return True
