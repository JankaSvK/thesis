import cv2

class TrackerPatternMatching(object):
    name = 'PATTERNMATCHING'

    def init(self, image, bbox):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.pattern = image[bbox[0]:bbox[2] + bbox[0], bbox[1]:bbox[3] + bbox[1]]
        self.height, self.width = self.pattern.shape
        return True

    def update(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(image, self.pattern, cv2.TM_CCOEFF)
        _, maxVal, _, maxLoc = cv2.minMaxLoc(res)

        return (True, (maxLoc[0], maxLoc[1], self.width, self.height))