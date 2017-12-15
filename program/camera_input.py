import numpy as np
import cv2
import time
from multiprocessing import Process, Queue


class VideoProvider(object):
    def __init__(self, cam_index):
        print("Initializing video provider")
        self.cam_index = cam_index

    def setup_camera(self, width, height):
        self.capture = cv2.VideoCapture(self.cam_index)
        assert self.capture.isOpened()

        self.capture.set(3,640)
        self.capture.set(4,480)

    def start_capturing(self):
        self.work = True
        self.capturing()

    def stop_capturing(self):
        self.work = False

    def capturing(self):
        while self.work:
            ret, frame = self.capture.read()
            if ret:
                print("Adding image")
                images.put(frame)

class CameraWrapper(object):
    def __init__(self, camera_index):
        self.camera_index = camera_index
        process = Process(target=self.run_camera)
        process.daemon = True
        process.start()

    def run_camera(self):
        provider = VideoProvider(self.camera_index)
        provider.setup_camera(640,480)
        self.running = True
        provider.start_capturing()

cameras = [1]
images = SimpleQueue()
if __name__ == '__main__':
    # spominane, ze len problem windowsov
    ## https://stackoverflow.com/questions/18204782/runtimeerror-on-windows-trying-python-multiprocessing

    wrap = CameraWrapper(cameras[0])

    time.sleep(2)

    print(images.empty())
    time.sleep(1)
    print(images.empty())

    time.sleep(1)
    CameraWrapper.running = False

    time.sleep(5)
    print(images.qsize())

    print("Stopping")


