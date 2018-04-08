import time
import threading

import cv2
import sys

from CustomTracker import CustomTracker
from TrackerSimpleBackground import TrackerSimpleBackground
from TtrackerHSV import TrackerHSV


class ComplexTracker:
    def __init__(self, camera_index, image_stream, tracked_points, tracker_type = None):
        if tracker_type is None:
            tracker_type = 'KCF'

        self.tracker = self.create_tracker(tracker_type)
        self.input = image_stream
        self.output = tracked_points
        self.camera_index = camera_index

    def set_initial_position(self, left_upper_corner, right_bottom_corner):
        x1, y1 = left_upper_corner['x'], left_upper_corner['y']
        x2, y2 = right_bottom_corner['x'], right_bottom_corner['y']

        self.initial_position = (x1, y1, x2 - x1, y2 - y1)

        print("Init called")
        if len(self.input) == 0:
            return False

        initial_image = self.input[-1][1]
        print("Non empty images")
        ok = self.tracker.init(initial_image, self.initial_position)
        print("Initialization", ok)

    def create_tracker(self, tracker_type): #TODO: vytiahnut do samostatneho suboru
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        elif tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        elif tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        elif tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        elif tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        #elif tracker_type == 'GOTURN': # Until bug is resolved, not usable
        #    tracker = cv2.TrackerGOTURN_create()
        elif tracker_type == 'CUSTOMTRACKER':
            tracker = CustomTracker()
        elif tracker_type == 'SIMPLEBACKGROUND':
            tracker = TrackerSimpleBackground()
        elif tracker_type == TrackerHSV.name:
            tracker = TrackerHSV()

        else:
            tracker = cv2.TrackerKCF_create()

        return tracker #prepisat to na enumerator

    def start_tracking(self, stop_event):
        self.stop_event = stop_event
        t = threading.Thread(target=self.tracking, args=())
        t.name = 'Tracker'+str(self.camera_index)
        t.setDaemon(True)
        t.start()
        print("Started thread")

    def tracking(self):
        while not self.stop_event.is_set():
            if len(self.input) == 0:
                continue
            (time, image) = self.input[-1]
            coords = self.find_object(image)

            if coords is not None:
                self.output.append((time, coords))

    def find_object(self, image):
        print(time.time())
        ok, bbox = self.tracker.update(image)

        if ok:
            x, y = int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2)
            return (x, y)
        else:
            return None