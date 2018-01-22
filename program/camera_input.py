import numpy as np
import cv2
import time
from collections import deque
import threading as t

class VideoProvider(object):
    def __init__(self, cam_index):
        print("Initializing video provider on camera ", cam_index)
        self.cam_index = cam_index
        self.capture = cv2.VideoCapture(self.cam_index)
        assert self.capture.isOpened()

    def setup_camera(self, width, height):
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def capturing(self, images):
        ret, frame = self.capture.read()
        if ret:
            images.append((time.time(), frame))

class CameraWrapper(object):
    def __init__(self, camera_index, images):
        self.camera_index = camera_index
        self.images = images

    def start_camera(self):
        self.stop_event = t.Event()
        self.thread = t.Thread(target=self.run_camera, args=(self.stop_event, self.images))
        self.thread.setDaemon(True)
        self.thread.start()

    def stop_camera(self):
        self.stop_event.set()
        self.thread.join()

    def run_camera(self, stop_event, images):
        provider = VideoProvider(self.camera_index)
        provider.setup_camera(640,480)
        while not stop_event.is_set():
            provider.capturing(images)
        provider.capture.release()

    def get_images(self, count):
        return [self.images[i] for i in range(-count, 0)]

def skip_first_images(images, count):
    [ images.popleft() for _ in range(count) ]

#################################################
################ Program ########################
#################################################

if __name__ == '__main__':
    cameras = [0]
    images = [deque([], maxlen=500) for camera in cameras]

    wrappers = []
    for i, camera in enumerate(cameras):
        wrappers.append(CameraWrapper(camera, images[i]))
        wrappers[i].start_camera(images[i])

    time.sleep(5)

    for wrap in wrappers:
        wrap.stop_capturing()

    print("Stopping cameras")

    for i, _ in enumerate(cameras):
        print(i, " ", len(images[i]))
        skip_first_images(images[i], 3)
        image = images[i].popleft()
        cv2.imshow('Image'+str(i)+' '+str(image[0]), image[1])

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("Closing windows")
