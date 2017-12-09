import numpy as np
import cv2
import glob


class ChessboardFinder(object):

    def __init__(self, chessboard_image):
        self.images = glob.glob(chessboard_image)
        self.objpoints = []
        self.imgpoints = []
        self.size = (7,9)

    def find_chessboad(self):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Chessboard size
        size = (7, 9)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((size[0] * size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:size[0], 0:size[1]].T.reshape(-1, 2)

        for fname in self.images:
            img = cv2.imread(fname)
            self.h, self.w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, self.size, None)

            # If found, add object points, image points (after refining them)
            if ret == True:
                self.objpoints.append(objp)
                # print(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                self.imgpoints.append(corners2)

                # Draw and display the corners
                cv2.drawChessboardCorners(img, size, corners2, ret)
                cv2.imshow('img', img)
                cv2.waitKey(00)

    def calibrate(self):
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs =\
            cv2.calibrateCamera(self.objpoints, self.imgpoints, (self.h,self.w), None, None)
        self.newcameramtx, self.roi =\
            cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, (self.h, self.h), 1, (self.h, self.w))

    def undistort(self, img_path):
        img = cv2.imread(img_path)
        return cv2.undistort(img, self.mtx, self.dist, None, self.mtx)

    def compute_error(self):
        mean_error = 0
        for point, rvec, tvec, imgpoint in zip(self.objpoints, self.rvecs, self.tvecs, self.imgpoints):
            imgpoints2, _ = cv2.projectPoints(point, rvec, tvec, self.mtx, self.dist)
            error = cv2.norm(imgpoint, imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error
        return mean_error / len(self.objpoints)



finders = [
    ChessboardFinder('images/single_camera_calibration/left/*.jpg'),
    #ChessboardFinder('images/single_camera_calibration/right/*.jpg'),
]

for finder in finders:
    finder.find_chessboad()

finders[0].calibrate()
print(finders[0].compute_error())
undistort = finders[0].undistort('images/single_camera_calibration/left/WIN_20171208_23_28_07_Pro.jpg')
cv2.imwrite('images/single_camera_calibration/calibresult.png', undistort)

cv2.destroyAllWindows()