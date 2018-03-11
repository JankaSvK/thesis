import threading

import cv2
import sys

class ComplexTracker:
    def __init__(self, camera_index, image_stream, output_stream, tracker_type = 'KCF'):
        self.tracker = self.create_tracker(tracker_type)
        self.tracking_history = []
        self.input = image_stream
        self.output = output_stream
        self.camera_index = camera_index

    def set_initial_position(self, left_upper_corner, right_bottom_corner):
        (x1, y1) = left_upper_corner
        (x2, y2) = right_bottom_corner

        self.initial_position = (x1, y1, x2, y2)

        print("Init called")
        if len(self.input) == 0:
            return False

        initial_image = self.input[-1][1]
        print("Non empty images")
        ok = self.tracker.init(initial_image, self.initial_position)
        print("Initialization", ok)

    def create_tracker(self, tracker_type):
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()

        return tracker #prepisat to na enumerator

    def start_tracking(self):
        t = threading.Thread(target=self.tracking, args=())
        t.name = 'Tracker-'+str(self.camera_index)
        t.daemon = True
        t.start()
        print("Started thread")

    def tracking(self):
        while True:
            if len(self.input) == 0:
                continue
            (time, image) = self.input[-1]
            coords = self.find_object(image)

            if coords is not None:
                self.output.append((time, coords))

    def find_object(self, image):
        ok, bbox = self.tracker.update(image)

        if ok:
            return (int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2))
        else:
            return None