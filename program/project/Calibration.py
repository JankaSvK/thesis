import numpy as np
import cv2

from CalibrationResults import MonoCameraCalibrationResults, StereoCameraCalibrationResults
from ChessboardPattern import ChessboardPattern


class MonoCameraCalibration(object):
    def __init__(self, images, chessboard_size, image_size):
        self.chessboard_size = chessboard_size
        self.images = images
        self.objpoints = []
        self.imgpoints = []
        self.successful = []
        self.image_size = image_size

        self.corners_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    def find_chessboad(self):
        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)

        for i, record in enumerate(self.images):
            img = record[1]
            self.h, self.w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, flags=cv2.CALIB_CB_FAST_CHECK)

            if ret:
                ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size)
                self.successful.append(i)
                self.objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), self.corners_criteria)
                self.imgpoints.append(corners2)

    def calibrate(self):
        ret, mtx, dist, rvecs, tvecs =\
            cv2.calibrateCamera(self.objpoints, self.imgpoints, self.image_size, None, None)
        if ret:
            self.calibration_results = MonoCameraCalibrationResults(mtx, dist, rvecs, tvecs)
        return ret

    def compute_error(self):
        mean_error = 0
        c = self.calibration_results
        for point, rvec, tvec, imgpoint in zip(self.objpoints, c.rotation_vec, c.translation_vec, self.imgpoints):
            imgpoints2, _ = cv2.projectPoints(point, rvec, tvec, c.camera_matrix, c.distortion_coeffs)
            error = cv2.norm(imgpoint, imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            mean_error += error
        return mean_error / len(self.objpoints)


class StereoCameraCalibration(object):
    def __init__(self, mono_calibrations: [MonoCameraCalibration]):
        self.imgpoints = [] # TODO, ma to byt list listov. na [0] maju byt imgpoints prvej kamery a [1] druhej
        self.mono_calibrations = mono_calibrations

        pattern = ChessboardPattern((6, 9), 30)
        self.object_points = pattern.get_object_points()

    def stereo_calibrate(self):
        results1 = self.mono_calibrations[0].calibration_results
        results2 = self.mono_calibrations[1].calibration_results

        reprerror, _, _, _, _, r, t, e, f =\
            cv2.stereoCalibrate(
                objectPoints=self.object_points,
                imagePoints1=self.imgpoints[0], imagePoints2=self.imgpoints[1],
                cameraMatrix1=results1.camera_matrix, distCoeffs1=results1.distortion_coeffs,
                cameraMatrix2=results2.camera_matrix, distCoeffs2=results2.distortion_coeffs,
                imageSize=(1,1), #should not be used, because intristic matrix is fixed
                criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
            )
        self.calibration_results = StereoCameraCalibrationResults(r, t, e, f, reprerror)