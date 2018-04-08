import time
import cv2
import numpy

from TrackingHelper import get_largest_contour

def get_average_angle(angles):
    angles = numpy.radians(angles)
    x, y = 0, 0
    for angle in angles:
        x += numpy.cos(angle)
        y += numpy.sin(angle)

    res = numpy.degrees(numpy.arctan2(y, x))
    if res < 0:
        return res + 360
    return res

class TrackerHSV(object):
    name = 'HSV'

    def __init__(self):
        pass

    def init(self, image, bbox):
        pattern = image[bbox[0]:bbox[2] + bbox[0], bbox[1]:bbox[3] + bbox[1]]
        hsv = cv2.cvtColor(pattern, cv2.COLOR_BGR2HSV)
        hues = hsv[:,:,0].flatten()
        self.most_common_color = get_average_angle(hues)

        self.lower_bound = numpy.array([self.most_common_color - 10, 50, 50])
        self.upper_bound = numpy.array([self.most_common_color + 10, 255, 255])
        return True

    def update(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_image, self.lower_bound, self.upper_bound) #TODO fixni cervenu
        largest_cnt = get_largest_contour(mask, 1000)
        if largest_cnt is not None:
            return (True, cv2.boundingRect(largest_cnt))
        return (False, None)

#
# cap = cv2.VideoCapture(0)
# ret, im = cap.read()
# cv2.imshow("Capture", im)
# tracker = TrackerHSV()
# tracker.init(im, (0, 0, 100, 100))
# time.sleep(1)
# ret, im = cap.read()
# print(tracker.update(im))