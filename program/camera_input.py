import numpy as np
import cv2
import time
from multiprocessing import Process


class VideoProvider(object):
    def __init__(self, cam_index):
        print("Initializing video provider")
        self.images = []
        self.cam_index = cam_index

    def setup_camera(self, width, height):
        self.capture = cv2.VideoCapture(self.cam_index)
        assert self.capture.isOpened()

        self.capture.set(3,640)
        self.capture.set(4,480)

    def start_capturing(self):
        self.work = True
        process = Process(target = self.capturing)
        process.daemon = True
        print("Starting process")
        process.start()

    def stop_capturing(self):
        self.work = False

    def capturing(self):
        while self.work:
            print("Capturing")
            ret, frame = self.capture.read()
            if ret:
                self.images.append(frame)


cameras = [1]
providers = [ VideoProvider(camera) for camera in cameras ]

for provider in providers:
    provider.setup_camera(640, 480)
    provider.start_capturing()
    provider.stop_capturing()

print("Stopping")


