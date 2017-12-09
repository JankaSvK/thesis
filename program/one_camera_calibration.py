import numpy as np
import cv2
import glob


class MonoCameraCalibration(object):

    def __init__(self, chessboard_image):
        self.name = chessboard_image
        self.images = glob.glob(chessboard_image)
        self.objpoints = []
        self.imgpoints = []
        self.size = (7,9)
        self.sucessful = []

    def find_chessboad(self):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Chessboard size
        size = (7, 9)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((size[0] * size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:size[0], 0:size[1]].T.reshape(-1, 2)

        for i, fname in enumerate(self.images):
            img = cv2.imread(fname)
            self.h, self.w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, self.size, None)

            # If found, add object points, image points (after refining them)
            if ret:
                self.sucessful.append(i)
                self.objpoints.append(objp)
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


class StereoCameraCalibration(object):
    def __init__(self, mono_calibrations: [MonoCameraCalibration]) -> object:
        self.mono_calibrations = mono_calibrations

    def combine(self):
        list(sorted(set.intersection(*[set(calibration.successful) for calibration in self.mono_calibrations])))



path_to_images = 'images/two_camera_calibration/'

finders = [
    MonoCameraCalibration(path_to_images + 'left/*.jpg'),
    MonoCameraCalibration(path_to_images + 'right/*.jpg'),
]

for finder in finders:
    print(finder.name)
    finder.find_chessboad()
    finder.calibrate()
    print(finder.sucessful)
    print(finder.compute_error())



#c1 = finders[0]
#c2 = finders[1]
#objpoints = []
#R = []
#T = []
#E = []
#F = []
#cv2.stereoCalibrate(objpoints, c1.imgpoints, c2.imgpoints, c1.mtx, c1.dist, c2.mtx, c2.dist, c1.size, R, T, E, F,
#                    cv2.cvTermCriteria(cv2.CV_TERMCRIT_ITER+cv2.CV_TERMCRIT_EPS, 100, 1e-5),
#                    cv2.CV_CALIB_SAME_FOCAL_LENGTH | cv2.CV_CALIB_ZERO_TANGENT_DIST)




#finders[0].calibrate()
#print(finders[0].compute_error())
#undistort = finders[0].undistort('images/single_camera_calibration/left/WIN_20171208_23_28_07_Pro.jpg')
#cv2.imwrite('images/single_camera_calibration/calibresult.png', undistort)

cv2.destroyAllWindows()