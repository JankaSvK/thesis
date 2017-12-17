import numpy as np
import cv2
import glob

chessboard_size = (7, 9)
image_size =  (640,480)

class MonoCameraCalibration(object):

    def __init__(self, chessboard_image):
        self.name = chessboard_image
        self.images = glob.glob(chessboard_image)
        self.objpoints = []
        self.imgpoints = []
        self.successful = []

    def find_chessboad(self):
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

        for i, fname in enumerate(self.images):
            img = cv2.imread(fname)
            self.h, self.w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(gray, chessboard_size, flags=cv2.CALIB_CB_FAST_CHECK)

            if ret:
                ret, corners = cv2.findChessboardCorners(gray, chessboard_size)
                self.successful.append(i)
                self.objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                self.imgpoints.append(corners2)

                # Draw and display the corners
                #cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
                #cv2.imshow('img', img)
                #cv2.waitKey(00)

    def calibrate(self):
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs =\
            cv2.calibrateCamera(self.objpoints, self.imgpoints, image_size, None, None)
        #self.mtx, self.roi =\
        #    cv2.getOptimalNewCameraMatrix(self.mtx, self.dist, image_size, 1, image_size)

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

        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

        [ self.objpoints.append(objp) for i in intersection ]

        for calibration in self.mono_calibrations:
            indices = [ calibration.successful.index(index) for index in intersection ]
            self.imgpoints.append([ calibration.imgpoints[i] for i in indices ])

    def stereo_calibrate(self):
        self.reprerror, self.mtx1, self.dst1, self.mtx2, self.dst2, self.r, self.t, self.e, self.f =\
            cv2.stereoCalibrate(
                objectPoints=self.objpoints,
                imagePoints1=self.imgpoints[0], imagePoints2=self.imgpoints[1],
                cameraMatrix1=self.mono_calibrations[0].mtx, distCoeffs1=self.mono_calibrations[0].dist,
                cameraMatrix2=self.mono_calibrations[1].mtx, distCoeffs2=self.mono_calibrations[1].dist,
                imageSize=(1,1),
                #flags=cv2.CALIB_USE_INTRINSIC_GUESS,
                criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
            )
        print("Reprojection Error", self.reprerror)
        self.R1, self.R2, self.P1, self.P2, self.Q, validPixROI1, validPixROI2 =\
            cv2.stereoRectify(self.mtx1, self.dst1, self.mtx2, self.dst2, image_size, self.r, self.t)
        print("R1", self.R1)
        print("R2", self.R2)
        print("P1", self.P1)
        print("P2", self.P2)
        print("r", self.r)
        print("t", self.t)


    def init_undistort(self):
        self.map1x, self.map1y = cv2.initUndistortRectifyMap(self.mtx1, self.dst1, self.R1, self.P1, image_size, cv2.CV_32FC1);
        self.map2x, self.map2y = cv2.initUndistortRectifyMap(self.mtx2, self.dst2, self.R2, self.P2, image_size, cv2.CV_32FC1);
        #cv2.initUndistortRectifyMap()

    def undistort(self, img1_path, img2_path):
        img1 = cv2.imread(img1_path)
        img2 = cv2.imread(img2_path)
        img1new = cv2.remap(img1, self.map1x, self.map1y, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT);
        img2new = cv2.remap(img2, self.map2x, self.map2y, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT);
        return img1new, img2new, img1, img2

#########################################################################
###########################  Program  ###################################
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

cv2.imshow('Undistort', finders[0].undistort(path_to_images + 'left/6.jpg'))

stereo_calibration = StereoCameraCalibration(finders)
stereo_calibration.combine()
stereo_calibration.stereo_calibrate()
stereo_calibration.init_undistort()
img1, img2, img1original, img2original = stereo_calibration.undistort(path_to_images + 'left/6.jpg', path_to_images + 'right/6.jpg')
cv2.imshow('img', img1)
cv2.imshow('img2', img2)
cv2.imshow('imgO', img1original)
cv2.imshow('img2O', img2original)

cv2.waitKey(00)


cv2.destroyAllWindows()

# Kolko obrazkov je dostatok?
### porovnat rotacnu matiacu a translacny vektor so skutocnostou (zmerat si o kolko sa to posunulo)

## Chcem vobec pouzivat rectify? Bude nutne?
## Pozriet sa na cisla z toho lezu, preco t v prehodenych kamera nema rovnaku normu
## Dava zmysel R, t? Distortion coeff. by mali byt blizke nule
## norma t by mala odpovedat vzdialenosti kamier
## ujasnit si suradnice

# Co je maly reprojection error u stereocalibration

# Nemam rovnaku velkost image z kamier, mam zjednotit?
# - zatial ano

# Ten vysledok asi nerobi nic dobreho.

# mozno pouzit tu vec s new optimal matrix

# pouzit fast na findchessboardcorners a v druhej vrstve hladat poriadne

# skusit na kamery
### nazbieravanie snimkov
### kalibracia stereo a mono na rovnakych snimkoch alebo roznych

# 1 . zmysluplne data
# 2 . "rozhranie" k pristupu datam
# 3 . spracovavanie z kamier

# 4 . GUI, opravit
