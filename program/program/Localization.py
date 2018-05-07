import cv2
import numpy as np
import os
from . import Config
from . import TrackersProvider
from .CalibrationResults import get_current_time
from .QueuesEntries import Point
from .QueuesProvider import QueuesProvider

class Localization(object):
    objects_count = Config.objects_count
    rotation_matrix1 = None
    rotation_matrix2 = None
    projection_matrix1 = None
    projection_matrix2 = None
    mono_calibration_results = None
    fundamental_matrix = None

    localization_precision = 5 # in millimeters
    last_located_point = None
    last_located_point_time = [-1 for i in range(objects_count)]
    time_threshold_skip = 1/20
    time_threshold_correspondence = 1/10

    @classmethod
    def compute_projection_matrices(cls, calibration_results1, calibration_results2, stereo_calibration_results):
        cls.mono_calibration_results = [calibration_results1, calibration_results2]
        cls.fundamental_matrix = stereo_calibration_results.fundamental_matrix

        rt = np.append(stereo_calibration_results.rotation_matrix, stereo_calibration_results.translation_vector, axis = 1)
        cls.projection_matrix2 = calibration_results2.camera_matrix.dot(rt)
        cls.projection_matrix1 = calibration_results1.camera_matrix.dot(np.eye(3, 4))

    @classmethod
    def get_3d_coordinates(cls, *points):
        if any(point is None for point in points) or len(points) != 2:
            return None

        # OpenCv function works with a set of points. In our case we have only one point per camera,
        # therefore we reshape into required format
        points = [np.array(point).reshape(1, 1, 2).astype(float) for point in points]
        points = [cls.get_undistorted_point(point, i) for i, point in enumerate(points)]

        locatedPointsHom = cv2.triangulatePoints(projMatr1=cls.projection_matrix1, projMatr2=cls.projection_matrix2,
                                                 projPoints1=points[0],
                                                 projPoints2=points[1])
        return cls.convert_from_homogenous(locatedPointsHom)

    @classmethod
    def get_undistorted_point(cls, point, cam_ind):
        calib_results = cls.mono_calibration_results[cam_ind]
        undistorted = cv2.undistortPoints(point, calib_results.camera_matrix, calib_results.distortion_coeffs,
                                          P=calib_results.camera_matrix) # without setting P normalized points would be returned
        return undistorted

    @classmethod
    def save_localization_data(cls):
        times = [x[0].timestamp for x in QueuesProvider.LocalizatedPoints3D if x]
        if times:
            first_point_time = min(times)
        else:
            return

        for i in range(cls.objects_count):
            if len(QueuesProvider.LocalizatedPoints3D[i]) == 0:
                return

            filename = "localization_data/" + get_current_time() + "-" + str(i + 1) + ".txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w') as output:
               for point in QueuesProvider.LocalizatedPoints3D[i]:
                   point.timestamp -= first_point_time
                   output.write(str(point) + '\n')

    @classmethod
    def localize_point(cls, object_id):
        points0 = QueuesProvider.TrackedPoints2D[(TrackersProvider.get_tracker_uid(0, object_id))]
        points1 = QueuesProvider.TrackedPoints2D[(TrackersProvider.get_tracker_uid(1, object_id))]

        if len(points0) == 0 or len(points1) == 0:
            return

        point1 = points0[-1]
        point2 = points1[-1]

        if abs(point1.timestamp - point2.timestamp) > cls.time_threshold_correspondence:
            return

        time = (point1.timestamp + point2.timestamp) / 2
        if time - cls.last_located_point_time[object_id] < cls.time_threshold_skip:
            return
        cls.last_located_point_time[object_id] = time

        located_point = Localization.get_3d_coordinates(point1.coordinates,
                                                        point2.coordinates)
        if located_point is None:
            return

        if cls.moved_more_than(cls.last_located_point, located_point, cls.localization_precision):
            point = Point(located_point, time)
            QueuesProvider.LocalizatedPoints3D[object_id].append(point)
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
