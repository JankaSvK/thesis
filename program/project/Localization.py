import cv2
import numpy as np
import os
from CalibrationResults import get_current_time
from CoordsWithTimestamp import CoordsWithTimestamp
from QueuesProvider import QueuesProvider, Camera


class Localization(object):
    rotation_matrix1 = None
    rotation_matrix2 = None
    projection_matrix1 = None
    projection_matrix2 = None

    localization_precision = 5 # in milimeters
    last_located_point = None

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
            cls.projection_matrix2 = calibration_results2.camera_matrix.dot(rt)
            cls.projection_matrix1 = calibration_results1.camera_matrix.dot(np.append(np.identity(3), np.zeros((3, 1)), axis = 1))

    @classmethod
    def get_3d_coordinates(cls, point1, point2):
        if point1 is None or point2 is None:
            return None

        locatedPointsHom = cv2.triangulatePoints(projMatr1=cls.projection_matrix1, projMatr2=cls.projection_matrix2,
                                                 projPoints1=point1,
                                                 projPoints2=point2)
        return cls.convert_from_homogenous(locatedPointsHom)

    @classmethod
    def save_localization_data(cls):
        if len(QueuesProvider.LocalizatedPoints3D) == 0:
            return

        filename = "localization_data/" + get_current_time() + ".txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w') as output:
           for position in QueuesProvider.LocalizatedPoints3D:
               output.write(str(position) + '\n')

    @classmethod
    def localize_point(cls):
        if len(Camera[0].tracked_points) == 0 or len(Camera[1].tracked_points) == 0:
            return

        point1 = Camera[0].tracked_points[-1]
        point2 = Camera[1].tracked_points[-1]

        if abs(point1[0] - point2[0]) > 1/10:
            return
            # TODO: find in past points the correct one

        located_point = Localization.get_3d_coordinates(Camera[0].tracked_points[-1][1],
                                                        Camera[1].tracked_points[-1][1])

        if located_point is None:
            return
        if cls.moved_more_than(cls.last_located_point, located_point, cls.localization_precision):
            # TODO: tricky - many positions at the same time
            with_timestamp = CoordsWithTimestamp(timestamp= (point1[0] + point2[0]) / 2, coords=located_point)
            QueuesProvider.LocalizatedPoints3D.append(with_timestamp)
            cls.last_located_point = located_point

    @classmethod
    def moved_more_than(cls, old, new, distance):
        return old is None or np.linalg.norm(new - old) > distance

    @classmethod
    def convert_from_homogenous(cls, coords):
        return (coords[:-1] / coords[-1])[:, 0]
