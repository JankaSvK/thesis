import numpy as np

chessboard_size = (7,9)
square_size = 30

def get_object_points():
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)*square_size
    return objp