import cv2
import numpy
import numpy as np
import os

import Config
import TrackersProvider
from CalibrationResults import get_current_time
from CoordsWithTimestamp import CoordsWithTimestamp
from QueuesProvider import QueuesProvider

class Localization(object):
    objects_count = Config.objects_count
    rotation_matrix1 = None
    rotation_matrix2 = None
    projection_matrix1 = None
    projection_matrix2 = None
    mono_calibration_results = None

    localization_precision = 5 # in milimeters
    last_located_point = None

    @classmethod
    def compute_projection_matrices(cls, calibration_results1, calibration_results2, stereo_calibration_results):
        cls.mono_calibration_results = [calibration_results1, calibration_results2]

        stereo_rectify = False

        if stereo_rectify:
            cls.rotation_matrix1, cls.rotation_matrix2, cls.projection_matrix1, cls.projection_matrix2, _, _, _ = cv2.stereoRectify(
                calibration_results1.camera_matrix, calibration_results1.distortion_coeffs,
                calibration_results2.camera_matrix, calibration_results2.distortion_coeffs,
                (640, 480), stereo_calibration_results.rotation_matrix, stereo_calibration_results.translation_vector, alpha=0)
        else:
            rt = np.append(stereo_calibration_results.rotation_matrix, stereo_calibration_results.translation_vector, axis = 1)
            cls.projection_matrix2 = calibration_results2.camera_matrix.dot(rt)
            cls.projection_matrix1 = calibration_results1.camera_matrix.dot(np.append(np.identity(3), np.zeros((3, 1)), axis = 1))

    @classmethod
    def get_3d_coordinates(cls, point1, point2):
        if point1 is None or point2 is None:
            return None

        point1 = cls.get_undistorted_point(point1, 0)
        point2 = cls.get_undistorted_point(point1, 1)

        locatedPointsHom = cv2.triangulatePoints(projMatr1=cls.projection_matrix1, projMatr2=cls.projection_matrix2,
                                                 projPoints1=point1,
                                                 projPoints2=point2)
        return cls.convert_from_homogenous(locatedPointsHom)

    @classmethod
    def get_undistorted_point(cls, point, cam_ind):
        calib_results = cls.mono_calibration_results[cam_ind]
        point = np.array(point).reshape(1, 1, 2).astype(float)
        undistorted = cv2.undistortPoints(point, calib_results.camera_matrix, calib_results.distortion_coeffs, P=calib_results.camera_matrix)
        return undistorted[0][0]

    @classmethod
    def save_localization_data(cls):
        for i in range(cls.objects_count):

            if len(QueuesProvider.LocalizatedPoints3D[i]) == 0:
                return

            filename = "localization_data/" + get_current_time() + "-" + str(i + 1) + ".txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w') as output:
               for position in QueuesProvider.LocalizatedPoints3D[i]:
                   output.write(str(position) + '\n')

    @classmethod
    def localize_point(cls, object_id):
        points0 = QueuesProvider.TrackedPoints2D[(TrackersProvider.get_tracker_uid(0, object_id))]
        points1 = QueuesProvider.TrackedPoints2D[(TrackersProvider.get_tracker_uid(1, object_id))]

        if len(points0) == 0 or len(points1) == 0:
            return

        point1 = points0[-1]
        point2 = points1[-1]

        if point1 is None or point2 is None or point1[0] is None or point2[0] is None:
            return

        if abs(point1[0] - point2[0]) > 1/10:
            return
            # TODO: find in past points the correct one

        located_point = Localization.get_3d_coordinates(point1[1],
                                                        point2[1])

        if located_point is None:
            return

        if cls.moved_more_than(cls.last_located_point, located_point, cls.localization_precision):
            # TODO: tricky - many positions at the same time
            with_timestamp = CoordsWithTimestamp(timestamp= (point1[0] + point2[0]) / 2, coords=located_point)
            QueuesProvider.LocalizatedPoints3D[object_id].append(with_timestamp)
            cls.last_located_point = located_point

    @classmethod
    def moved_more_than(cls, old, new, distance):
        return old is None or np.linalg.norm(new - old) > distance

    @classmethod
    def convert_from_homogenous(cls, coords):
        return (coords[:-1] / coords[-1])[:, 0]

    @classmethod
    def get_camera_positions(cls, rotation_matrix, translation_vector):
        vector_length = 500
        camera1 = [[0, 0, 0], [0, 0, vector_length]]

        rotated_vector = rotation_matrix.dot(np.array([[0, 0, vector_length]]).T) + translation_vector
        camera2 = [translation_vector.T.tolist()[0], rotated_vector.T.tolist()[0]]
        return camera1, camera2
