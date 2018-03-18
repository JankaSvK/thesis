import logging
import cv2

import ChessboardPattern
from CalibrationResults import MonoCameraCalibrationResults, StereoCameraCalibrationResults


def check_chessboard(image, chessboard_size = None):
    # je image obrakzkom?


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if chessboard_size is None:
        chessboard_size = ChessboardPattern.chessboard_size
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, flags=cv2.CALIB_CB_FAST_CHECK)
    return (ret, corners, gray)

class MonoCameraCalibration(object):
    def __init__(self, chessboard_size, image_size):
        self.chessboard_size = chessboard_size
        self.image_size = image_size
        self.corners_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.calibration_results = None

    def find_chessboad(self, images, fastCheck = False):
        successful = 0
        objp = ChessboardPattern.get_object_points()

        objpoints = []
        imgpoints = []

        for i, record in enumerate(images):
            img = record[1] # omit time on the first position
            self.h, self.w = img.shape[:2]
            ret, corners, gray = check_chessboard(img)

            if ret:
                successful += 1
                if fastCheck:
                    ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, flags=cv2.CALIB_CB_FAST_CHECK)
                else:
                    ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size)

                if not ret or len(corners) != len(objp):
                    continue

                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), self.corners_criteria)
                imgpoints.append(corners2)
        logging.info("Chessboard found on {} out of {} images.".format(successful, len(images)))
        return (imgpoints, objpoints)


    def calibrate(self, images):
        (imgpoints, objpoints) = self.find_chessboad(images)

        if imgpoints == [] or len(imgpoints) != len(objpoints) or len(imgpoints) < 20:
            return False

        if len(imgpoints) > 50 and len(objpoints) > 50:
            imgpoints = imgpoints[0:50]
            objpoints = objpoints[0:50]

        for i in range(len(imgpoints)): # to je ze sa zle nacita
            if len(imgpoints[i]) != len(objpoints[i]):
                del(imgpoints[i])
                del(objpoints[i])

        success, mtx, dist, rvecs, tvecs =\
            cv2.calibrateCamera(objpoints, imgpoints, self.image_size, None, None)
        if success:
            self.calibration_results = MonoCameraCalibrationResults(mtx, dist, rvecs, tvecs)
            logging.info("\nCamera matrix\n{}\nDistortion coefficients\n{}".format(mtx, dist))
        return success

class StereoCameraCalibration(object):
    def __init__(self, mono_calibrations: [MonoCameraCalibration], imgpoint1, imgpoints2, objpoints):
        self.imgpoints = [] # TODO, ma to byt list listov. na [0] maju byt imgpoints prvej kamery a [1] druhej
        self.mono_calibrations = mono_calibrations
        self.object_points = objpoints
        self.imgpoints = (imgpoint1, imgpoints2)

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
                criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 1e-5)
            )
        self.calibration_results = StereoCameraCalibrationResults(r, t, e, f, reprerror)