#background tracker for now
import cv2

class Tracker(object):
    def initTracker(self, background_image):
        self.background = background_image
    
    def getCoords(self, image):
        diff = cv2.absdiff(self.background, image)
        diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
        _, diff = cv2.threshold(diff, 30, 255, 0)

        im2, contours, hierarchy = cv2.findContours(diff, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        largest_area = 0
        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                continue

            if largest_area < cv2.contourArea(contour):
                 largest_cnt = contour
                 largest_area = cv2.contourArea(contour)

        if largest_area > 0:
            (x, y, w, h) = cv2.boundingRect(largest_cnt)
            return (int(x + w/2), int(y + h/2))
        return None