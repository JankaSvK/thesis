class MonoCameraCalibrationResults(object):
    def __init__(self, camera_matrix, distortion_coeffs, rotation_vecs, translation_vecs):
        self.camera_matrix = camera_matrix
        self.distortion_coeffs = distortion_coeffs
        self.rotation_vec = rotation_vecs
        self.translation_vec = translation_vecs

class StereoCameraCalibrationResults(object):
    def __init__(self, rotation_matrix, translation_matrix, essential_matrix, fundamental_matrix, reprojection_error):
        self.rotation_matrix = rotation_matrix
        self.translation_matrix = translation_matrix
        self.essential_matrix = essential_matrix
        self.fundamental_matrix = fundamental_matrix

        self.reprojection_error = reprojection_error

    def __str__(self):
        output = "Rotation matrix\n" + str(self.rotation_matrix)
        output += "\nTranslation matrix\n" + str(self.translation_matrix)
        output += "\nEnssential matrix\n" + str(self.essential_matrix)
        output += "\nFundamental matrix\n" + str(self.fundamental_matrix)
        output += "\nReprojection error\n" + str(self.reprojection_error)
        return output