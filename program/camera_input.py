import numpy as np
import cv2
import time
import queue as q
import threading as t

class VideoProvider(object):
    def __init__(self, cam_index):
        print("Initializing video provider")
        self.cam_index = cam_index
        self.capture = cv2.VideoCapture(self.cam_index)
        time.sleep(1)
        assert self.capture.isOpened()

    def setup_camera(self, width, height):
        self.capture.set(3,640)
        self.capture.set(4,480)

    def capturing(self, images):
        ret, frame = self.capture.read()
        if ret:
            images.put(frame, False)

class CameraWrapper(object):
    def __init__(self, camera_index, images):
        self.camera_index = camera_index
        self.stop_event = t.Event()
        self.thread = t.Thread(target=self.run_camera, args=(self.stop_event,images))
        self.thread.setDaemon(True)
        self.thread.start()

    def stop_camera(self):
        self.stop_event.set()
        self.thread.join()

    def run_camera(self, stop_event, images):
        print("Here1")
        provider = VideoProvider(self.camera_index)
        provider.setup_camera(640,480)
        print("Here2")
        while not stop_event.is_set():
            provider.capturing(images)
        print("Here3")
        provider.capture.release()

def skip_first_images(images, count):
    [ images.get() for i in range(count) ]

cameras = [0,1]
images = [q.Queue() for camera in cameras]

wrappers = []
for i, camera in enumerate(cameras):
    wrappers.append(CameraWrapper(camera, images[i]))

time.sleep(5)

for wrap in wrappers:
    wrap.stop_camera()

print("Stopping cameras")

for i, _ in enumerate(cameras):
    print(i, " ", images[i].qsize())
    skip_first_images(images[i], 3)
    image = images[i].get()
    cv2.imshow('Image'+str(i), image)

cv2.waitKey(0)
cv2.destroyAllWindows()
print("Closing windows")