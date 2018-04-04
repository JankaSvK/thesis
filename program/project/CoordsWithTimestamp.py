import time

class CoordsWithTimestamp(object):
    def __init__(self, coords, timestamp = None):
        if timestamp is None:
            timestamp = time.time()
        self.time = timestamp
        self.coords = coords

    def __str__(self):
        return '({}, {})'.format(self.time, self.coords)
