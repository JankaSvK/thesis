import json
import os

from datetime import datetime
import numpy

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d-at-%H-%M")

def import_json(object, jsonFile):
    with open(jsonFile, 'r') as input:
        object.__dict__ = json.load(input)

class MonoCameraCalibrationResults(object):
    def __init__(self, camera_matrix = None, distortion_coeffs = None, rotation_vecs = None, translation_vecs = None, jsonFile = None):
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

        filename = "calib_results/" + str(camera_index + 1) + "/" + get_current_time() +".json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w') as output:
            json.dump(result, output)

class StereoCameraCalibrationResults(object):
    def __init__(self, rotation_matrix = None, translation_matrix = None, essential_matrix = None, fundamental_matrix = None, reprojection_error = None, jsonFile = None):
        if jsonFile is not None:
            import_json(self, jsonFile)

            self.rotation_matrix = numpy.array(self.rotation_matrix)
            self.translation_matrix = numpy.array(self.translation_matrix)
        else:
            self.rotation_matrix = rotation_matrix
            self.translation_matrix = translation_matrix
            self.essential_matrix = essential_matrix
            self.fundamental_matrix = fundamental_matrix

            self.reprojection_error = reprojection_error

    def camera_distance(self):
        return numpy.linalg.norm(self.translation_matrix)

    def save(self):
        result = {}

        for key in self.__dict__:
            if isinstance(self.__dict__[key], numpy.ndarray):
                result[key] = (self.__dict__[key]).tolist()
            else:
                result[key] = self.__dict__[key]

        filename = "calib_results/stereo_calib_results/" + get_current_time() +".json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w') as output:
            json.dump(result, output)


    def __str__(self):
        output = "Rotation matrix\n" + str(self.rotation_matrix)
        output += "\nTranslation matrix\n" + str(self.translation_matrix)
        output += "\nEnssential matrix\n" + str(self.essential_matrix)
        output += "\nFundamental matrix\n" + str(self.fundamental_matrix)
        output += "\nReprojection error\n" + str(self.reprojection_error)
        return output

