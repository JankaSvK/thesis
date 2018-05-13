import os
import json
import numpy
from datetime import datetime


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d-at-%H-%M")

class CalibrationImportError(RuntimeError):
    pass

def import_json(object, jsonFile):
    try:
        with open(jsonFile, 'r') as input:
            object.__dict__ = json.load(input)
    except:
        raise CalibrationImportError

class MonoCameraCalibrationResults(object):
    def __init__(self, camera_matrix=None, distortion_coeffs=None, rotation_vecs=None, translation_vecs=None,
                 jsonFile=None):
        if jsonFile is not None:
            import_json(self, jsonFile)
            self.camera_matrix = numpy.array(self.camera_matrix)
            self.distortion_coeffs = numpy.array(self.distortion_coeffs)
        else:
            self.camera_matrix = camera_matrix
            self.distortion_coeffs = distortion_coeffs
            self.rotation_vec = rotation_vecs
            self.translation_vec = translation_vecs

    def __str__(self):
        output = "Camera matrix\n" + str(self.camera_matrix)
        output += "\nDistortion coeffs\n" + str(self.distortion_coeffs)
        output += "\nRotation vector\n" + str(self.rotation_vec)
        output += "\nTranslation vector\n" + str(self.translation_vec)
        return output

    def save(self, camera_index):
        result = {}

        for key in self.__dict__:
            if isinstance(self.__dict__[key], list) or self.__dict__[key] is None:
                result[key] = None
            else:
                result[key] = (self.__dict__[key]).tolist()

        curr_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(curr_dir, "calib_results", str(camera_index + 1), '{}.json'.format(get_current_time()))
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w') as output:
            json.dump(result, output)


class StereoCameraCalibrationResults(object):
    def __init__(self, rotation_matrix=None, translation_vector=None, essential_matrix=None, fundamental_matrix=None,
                 reprojection_error=None, jsonFile=None):
        if jsonFile is not None:
            import_json(self, jsonFile)

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

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w') as output:
            json.dump(result, output)

    def __str__(self):
        output = "Rotation matrix\n" + str(self.rotation_matrix)
        output += "\nTranslation vector\n" + str(self.translation_vector)
        output += "\nEnssential matrix\n" + str(self.essential_matrix)
        output += "\nFundamental matrix\n" + str(self.fundamental_matrix)
        output += "\nReprojection error\n" + str(self.reprojection_error)
        return output
