import cv2
import numpy as np


class Localization(object):
    rotation_matrix1 = None
    rotation_matrix2 = None
    projection_matrix1 = None
    projection_matrix2 = None

    @classmethod
    def compute_projection_matrices(cls, calibration_results1, calibration_results2, stereo_calibration_results):
        stereo_rectify = False

        if stereo_rectify:
            cls.rotation_matrix1, cls.rotation_matrix2, cls.projection_matrix1, cls.projection_matrix2, _, _, _ = cv2.stereoRectify(
                calibration_results1.camera_matrix, calibration_results1.distortion_coeffs,
                calibration_results2.camera_matrix, calibration_results2.distortion_coeffs,
                (640, 480), stereo_calibration_results.rotation_matrix, stereo_calibration_results.translation_matrix, alpha=0)
        else:
            rt = np.append(stereo_calibration_results.rotation_matrix, stereo_calibration_results.translation_matrix, axis = 1)
            cls.projection_matrix1 = calibration_results1.camera_matrix.dot(rt)
            cls.projection_matrix2 = calibration_results2.camera_matrix.dot(np.append(np.identity(3), np.zeros((3, 1)), axis = 1))

    @classmethod
    def get_3d_coordinates(cls, point1, point2):
        locatedPointsHom = cv2.triangulatePoints(projMatr1=cls.projection_matrix1, projMatr2=cls.projection_matrix2,
                                                 projPoints1=point1,
                                                 projPoints2=point2)
        locatedPoint = (locatedPointsHom[:-1] / locatedPointsHom[-1])[:, 0]

        return locatedPoint

    @classmethod
    def start_localization(cls):
        pass

