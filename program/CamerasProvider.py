import cv2
import threading as t
import Config
from Image import Image
import time


class CamerasProvider(object):
    def __init__(self, images_queues, stop_event, console_output, camera_indexes = None, video_recordings = None):
        self.camera_indexes = camera_indexes
        self.images = images_queues
        self.captures = []
        self.width = None
        self.height = None
        self.fps = [None, None]
        self.stop_event = stop_event
        self.capturing_thread = None
        self.width = Config.image_width
        self.height = Config.image_height
        self.start_of_the_thread = None
        self.console_output = console_output

        if video_recordings is None and camera_indexes is None:
            raise RuntimeError("Camera source has to be specified")

        self.video_recordings = video_recordings
        self.camera_indexes = camera_indexes

    def initialize_capturing(self):
        if self.video_recordings is None:
            if len(self.camera_indexes) != Config.camera_count():
                raise RuntimeError("Two camera indexes has to be specified.")

            for i in self.camera_indexes:
                self.captures.append(cv2.VideoCapture(self.camera_indexes[i]))
        else:
            if len(self.video_recordings) != Config.camera_count():
                raise RuntimeError("Two video files has to be specified.")

            for video in self.video_recordings:
                self.captures.append(cv2.VideoCapture(video))

        self.setup_cameras()


    def start_capturing(self):
        if self.video_recordings is None:
            self.capturing_thread = t.Thread(target=self.capture_live, args=(), name="VideoCapture")
        else:
            self.capturing_thread = t.Thread(target=self.capture_from_videos, args=(), name="VideoCapture")

        self.capturing_thread.setDaemon(True)
        self.start_of_the_thread = time.time()
        self.capturing_thread.start()

    def stop_capturing(self):
        for i, capture in enumerate(self.captures):
            capture.release()
            print("Camera", i, "released.")

    def capture_live(self):
        while not self.stop_event.is_set():
            for i, capture in enumerate(self.captures):
                self.capture_and_save_image(i)
        self.stop_capturing()

    def capture_from_videos(self):
        self.number_of_read = [0, 0]
        while not self.stop_event.is_set():
            times = [self.number_of_read[i] / self.fps[i] for i in range(2)]
            shorter = int(times[0] > times[1]) # get index of minimum

            time_to_sleep = times[shorter] - (time.time() - self.start_of_the_thread)
            if time_to_sleep > 0.01:
                time.sleep(time_to_sleep) # to not have faster videos than reality

            self.number_of_read[shorter] += 1
            ok = self.capture_and_save_image(shorter)
            if not ok:
                self.console_output.append("Video ended.")
                break
        self.stop_capturing()

    def capture_and_save_image(self, cam_index):
        ok, frame = self.captures[cam_index].read()
        if ok:
            image = Image(time = time.time(), image=frame, chessboard=None)
            if self.stop_event.is_set():
                return False
            self.images[cam_index].append(image)
            return True
        else:
            return False

    def setup_cameras(self):
        for cam_ind, capture in enumerate(self.captures):
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            capture.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # turn the autofocus off
            #capture.set(cv2.CAP_PROP_SETTINGS, 1) # open properties window

            self.fps[cam_ind] = capture.get(cv2.CAP_PROP_FPS)