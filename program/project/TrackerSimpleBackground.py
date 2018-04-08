import time
import cv2
import numpy

from TrackingHelper import get_largest_contour


class TrackerSimpleBackground(object):
    name = 'SIMPLEBACKGROUND'

    def __init__(self, blur_size = (10, 10), threshold = 100, ignored_size_of_contour = 1000):
        self.blur_size = blur_size
        self.threshold = threshold
        self.ignored_size_of_contour = ignored_size_of_contour

    def init(self, image, bbox):
        self.original = image
        return True

    def update(self, image):
        print(time.time())

        diff = cv2.absdiff(self.original, image)
        diff = numpy.sum(diff, 2)

        diff = (diff > self.threshold).astype(numpy.uint8) * 255  # thresholding image
        diff = cv2.blur(diff, self.blur_size)   # reducing noise
        diff = (diff > self.threshold).astype(numpy.uint8) * 255  # thresholding image

        im2, cnts, hierarchy = cv2.findContours(diff, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        largest = get_largest_contour(cnts, self.ignored_size_of_contour)
        if largest is not None:
            return (True, cv2.boundingRect(largest))
        return (False, None)