import json
import os
from datetime import datetime

import numpy


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d-at-%H-%M")


class CalibrationImportError(RuntimeError):
    pass


def import_json(target, json_file):
    '''Maps imported json to variables of the instance'''
    try:
        with open(json_file, 'r') as i:
            target.__dict__ = json.load(i)
    except:
        raise CalibrationImportError

def save_to_json(source, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as output:
        json.dump(source, output)


class MonoCameraCalibrationResults(object):
    '''Class to store all mono calibration results'''
    def __init__(self, camera_matrix=None, distortion_coeffs=None, rotation_vecs=None, translation_vecs=None,
                 json_file=None):
        if json_file is not None:
            import_json(self, json_file)
            self.camera_matrix = numpy.array(self.camera_matrix)
            self.distortion_coeffs = numpy.array(self.distortion_coeffs)
        else:
            self.camera_matrix = camera_matrix
            self.distortion_coeffs = distortion_coeffs
            self.rotation_vec = rotation_vecs
            self.translation_vec = translation_vecs

    def __str__(self):
        return "Camera matrix\n" \
               "{}\n" \
               "Distortion coefficients\n" \
               "{}\n" \
               "Rotation matrix\n" \
               "{}\n" \
               "Translation vector\n" \
               "{}\n".format(self.camera_matrix, self.distortion_coeffs, self.rotation_vec, self.translation_vec)

    def save(self, camera_index):
        """Saves the mono calibration results to a json"""
        result = {}

        for key in self.__dict__:
            if isinstance(self.__dict__[key], list) or self.__dict__[key] is None:
                result[key] = None
            else:
                result[key] = (self.__dict__[key]).tolist()

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(curr_dir, "calib_results", str(camera_index + 1), '{}.json'.format(get_current_time()))

        save_to_json(result, filename)


class StereoCameraCalibrationResults(object):
    '''Class for storing stereo calibration results'''
    def __init__(self, rotation_matrix=None, translation_vector=None, essential_matrix=None, fundamental_matrix=None,
                 reprojection_error=None, json_file=None):
        if json_file is not None:
            import_json(self, json_file)

            self.rotation_matrix = numpy.array(self.rotation_matrix)
            self.translation_vector = numpy.array(self.translation_vector)
            self.fundamental_matrix = numpy.array(self.fundamental_matrix)
            self.essential_matrix = numpy.array(self.essential_matrix)
        else:
            self.rotation_matrix = rotation_matrix
            self.translation_vector = translation_vector
            self.essential_matrix = essential_matrix
            self.fundamental_matrix = fundamental_matrix

            self.reprojection_error = reprojection_error

    def camera_distance(self):
        '''Computes the norm of the transaltion vector -- distances between the cameras'''
        return numpy.linalg.norm(self.translation_vector)

    def save(self):
        result = {}

        for key in self.__dict__:
            if isinstance(self.__dict__[key], numpy.ndarray):
                result[key] = (self.__dict__[key]).tolist()
            else:
                result[key] = self.__dict__[key]

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(curr_dir, "calib_results", "stereo_calib_results", '{}.json'.format(get_current_time()))

        save_to_json(result, filename)

    def __str__(self):
        return "Rotation matrix\n" \
               "{}\n" \
               "Translation vector\n" \
               "{}\n" \
               "Essential matrix\n" \
               "{}\n" \
               "Fundamental matrix\n" \
               "{}\n" \
               "Reprojection error {}\n".format(self.rotation_matrix, self.translation_vector, self.essential_matrix,
                                                self.fundamental_matrix, self.reprojection_error)