import logging
from collections import deque

import cv2
import time
import threading as t

class CameraProvider(object):
    def __init__(self, images, camera_index, camera_name = None):
        logging.info("Initializing camera provider on camera index `{}`".format(camera_index))

        if not camera_name:
            camera_name = "Camera" + str(camera_index)

        self.images = images
        self.camera_index = camera_index
        self.camera_name = camera_name
        self.video_capture = cv2.VideoCapture(self.camera_index)

        #TODO: not to assert, but throw an exception and handle it
        #assert self.video_capture.isOpened()
        logging.info("Camera `{}` on index `{}` initialized successfully".format(self.camera_name, self.camera_index))

    def setup_camera(self, width, height):
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def start_capturing(self):
        logging.info("Camera `{}` on index `{}` starting.".format(self.camera_name, self.camera_index))
        self.stop_event = t.Event()
        self.thread = t.Thread(target=self.capture_image, args=(self.stop_event, self.images))
        #TODO: do I want it?
        #self.thread.setDaemon(True)
        self.thread.start()

    def stop_capturing(self):
        logging.info("Camera `{}` on index `{}` stopping.".format(self.camera_name, self.camera_index))
        self.stop_event.set()
        self.thread.join()

    def capture_image(self, stop_event, images):
        while not stop_event.is_set():
            ret, frame = self.video_capture.read()
            if ret:
                images.append((time.time(), frame))

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