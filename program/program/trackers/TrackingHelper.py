import numpy
import cv2

def get_largest_contour(mask, ignored_size):
    if len(mask) == 0:
        return None
    im2, cnts, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    largest_area, largest_cnt = 0, None
    for c in cnts:
        if cv2.contourArea(c) < ignored_size:
            continue

        if largest_area < cv2.contourArea(c):
            largest_cnt = c
            largest_area = cv2.contourArea(c)

    return largest_cnt

