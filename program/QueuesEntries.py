import time


class Point(object):
    def __init__(self, coordinates, timestamp=None):
        self.timestamp = timestamp
        self.coordinates = coordinates

        if self.timestamp is None:
            self.timestamp = time.time()


class ImageEntry(object):
    def __init__(self, image, timestamp=None):
        self.timestamp = timestamp
        self.image = image

        if self.timestamp is None:
            self.timestamp = time.time()

        self._chessboard = None
        self._chessboard_checked = False

    def add_chessboard(self, chessboard):
        self._chessboard = chessboard
        self._chessboard_checked = True

    def contains_chessboard(self):
        return True if self._chessboard is not None else False

    def chessboard_checked(self):
        return self._chessboard_checked

