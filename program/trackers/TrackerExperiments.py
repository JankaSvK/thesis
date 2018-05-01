class TrackerExperiments(object):
    def __init__(self):
        self.position = None

    def init(self, image, bbox):
        self.position = (bbox[0], bbox[1])
        return True

    def update(self, image):
        return True, (self.position[0], self.position[1], 1, 1)