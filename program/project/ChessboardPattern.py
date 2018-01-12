import numpy as np

class ChessboardPattern(object):
    def __init__(self, chessboard_size, square_size):
        self.chessboard_size = chessboard_size
        self.square_size = square_size

    def get_object_points(self):
        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)*self.square_size
        return objp