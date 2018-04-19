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

    def __init__(self, color_tolerancy = 10, ignored_countours = 1000):
        self.ignored_countours = ignored_countours
        self.color_tolerancy = color_tolerancy

        self.bottom_saturation = 50
        self.upper_saturation = 255

        self.bottom_value = 50
        self.upper_value = 255

        self.lowest_point = [0, self.bottom_saturation, self.bottom_value]
        self.highest_point = [179, self.upper_saturation, self.upper_value]

    def init(self, image, bbox):
        pattern = image[bbox[1]:bbox[3] + bbox[1], bbox[0]:bbox[2] + bbox[0]] # swapping x and y, since matrix representation have columns first
        hsv = cv2.cvtColor(pattern, cv2.COLOR_BGR2HSV)
        hues = hsv[:,:,0].flatten()
        self.most_common_color = get_average_angle(hues)

        self.lower_bound = numpy.array([self.most_common_color - self.color_tolerancy, self.bottom_saturation, self.bottom_value])
        self.upper_bound = numpy.array([self.most_common_color + self.color_tolerancy, self.upper_saturation, self.upper_value])
        return True

    def update(self, image):
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv_image, self.lower_bound, self.upper_bound)
        if self.lower_bound[0] < 0 or self.upper_bound[0] >= 180:
            if self.lower_bound[0] < 0:
                mask_add = cv2.inRange(hsv_image, [180, 0, 0] + self.lower_bound, self.highest_point)
            else:
                mask_add = cv2.inRange(hsv_image, self.lowest_point, self.upper_bound - [180, 0, 0])
            mask = cv2.bitwise_or(mask_add, mask)

        largest_cnt = get_largest_contour(mask, self.ignored_countours)
        if largest_cnt is not None:
            return (True, cv2.boundingRect(largest_cnt))
        return (False, None)