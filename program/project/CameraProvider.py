import logging
from collections import deque

import cv2
import time
import threading as t

class CameraProvider(object):
    def __init__(self, images, camera_index, camera_name = None, video_recording = None):
        logging.info("Initializing camera provider on camera index `{}`".format(camera_index))

        if not camera_name:
            camera_name = "Camera" + str(camera_index)

        self.images = images
        self.camera_index = camera_index
        self.camera_name = camera_name
        if video_recording is not None:
            self.video_capture = cv2.VideoCapture(video_recording)
            self.video_recording = True
        else:
            self.video_recording = False
            self.video_capture = cv2.VideoCapture(self.camera_index)

        logging.info("Camera `{}` on index `{}` initialized successfully".format(self.camera_name, self.camera_index))

    def setup_camera(self, width, height):
        self.width = width
        self.height = height

        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.fps = self.video_capture.get(cv2.CAP_PROP_FPS)

    def start_capturing(self, stop_event):
        logging.info("Camera `{}` on index `{}` starting.".format(self.camera_name, self.camera_index))
        self.stop_event = stop_event
        self.thread = t.Thread(target=self.capture_image, args=(self.stop_event, self.images), name="Camera" + str(self.camera_index))
        self.thread.setDaemon(True)
        self.thread.start()

    def stop_capturing(self):
        logging.info("Camera `{}` on index `{}` stopping.".format(self.camera_name, self.camera_index))
        self.stop_event.set()
        self.thread.join()

    def capture_image(self, stop_event, images):
        while not stop_event.is_set():
            ret, frame = self.video_capture.read()
            if ret:
                if self.video_recording:
                    frame = cv2.resize(frame, (self.width, self.height))
                    images.append((time.time(), frame))
                    time.sleep(1 / self.fps)
                else:
                    images.append((time.time(), frame))
            else:
                stop_event.set()
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.video_capture.release()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    q = deque([], maxlen=500)
    provider = CameraProvider(camera_index=0, camera_name="PC camera", images=q)

    provider.setup_camera(640, 480)
    provider.start_capturing()
    time.sleep(5)
    provider.stop_capturing()