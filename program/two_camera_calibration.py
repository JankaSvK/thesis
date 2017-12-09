import numpy as np
import cv2
import glob

# Chessboard size
size = (7, 9)


class MonoCameraCalibration(object):

    def __init__(self, chessboard_image):
        self.name = chessboard_image
        self.images = glob.glob(chessboard_image)
        self.objpoints = []
        self.imgpoints = []
        self.size = (7,9)
        self.successful = []

    def find_chessboad(self):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

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
                self.successful.append(i)
                self.objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                self.imgpoints.append(corners2)

                # Draw and display the corners
                #cv2.drawChessboardCorners(img, size, corners2, ret)
                #cv2.imshow('img', img)
                #cv2.waitKey(00)

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
        self.imgpoints = []
        self.mono_calibrations = mono_calibrations
        self.objpoints = []

    def combine(self):
        intersection = list(sorted(
            set.intersection(*[set(calibration.successful) for calibration in self.mono_calibrations])))

        objp = np.zeros((size[0] * size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:size[0], 0:size[1]].T.reshape(-1, 2)

        [ self.objpoints.append(objp) for i in intersection ]

        for calibration in self.mono_calibrations:
            indices = [ calibration.successful.index(index) for index in intersection ]
            self.imgpoints.append([ calibration.imgpoints[i] for i in indices ])

    def stereo_calibrate(self):
#        R, T, E, F = [], [], [], []

        self.reprerror, self.mtx1, self.dst1, self.mtx2, self.dst2, self.r, self.t, self.e, self.f =\
            cv2.stereoCalibrate(
                objectPoints=self.objpoints,
                imagePoints1=self.imgpoints[0], imagePoints2=self.imgpoints[1],
                cameraMatrix1=self.mono_calibrations[0].mtx, distCoeffs1=self.mono_calibrations[0].dist,
                cameraMatrix2=self.mono_calibrations[1].mtx, distCoeffs2=self.mono_calibrations[1].dist,
                imageSize=(1,1),
                criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
            )

        self.R1, self.R2, self.P1, self.P2, self.Q, validPixROI1, validPixROI2 =\
            cv2.stereoRectify(self.mtx1, self.dst1, self.mtx2, self.dst2, (640, 480), self.r, self.t)

    def init_undistort(self):
        self.map1x, self.map1y = cv2.initUndistortRectifyMap(self.mtx1, self.dst1, self.R1, self.P1, (640,480), cv2.CV_32FC1);
        self.map2x, self.map2y = cv2.initUndistortRectifyMap(self.mtx2, self.dst2, self.R2, self.P2, (640,480), cv2.CV_32FC1);

    def undistort(self, img1_path, img2_path):
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        img1new = cv2.remap(img1, self.map1x, self.map1y, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT);
        img2new = cv2.remap(img2, self.map2x, self.map2y, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT);
        return img1new, img2new

#########################################################################
#########################################################################
#########################################################################

path_to_images = 'images/two_camera_calibration/'

finders = [
    MonoCameraCalibration(path_to_images + 'left/*.jpg'),
    MonoCameraCalibration(path_to_images + 'right/*.jpg'),
]

for finder in finders:
    print(finder.name)
    finder.find_chessboad()
    finder.calibrate()
    print(finder.successful)
    print(finder.compute_error())

stereo_calibration = StereoCameraCalibration(finders)
stereo_calibration.combine()
stereo_calibration.stereo_calibrate()
stereo_calibration.init_undistort()
img1, img2 = stereo_calibration.undistort(path_to_images + 'left/1.jpg', path_to_images + 'right/1.jpg')
cv2.imshow('img', img1)
cv2.imshow('img2', img2)
cv2.waitKey(00)


cv2.destroyAllWindows()

# Kolko obrazkov je dostatok?
# Co je maly reprojection error u stereocalibration
# Nemam rovnaku velkost image z kamier, mam zjednotit?
# Ten vysledok asi nerobi nic.