import logging
import time
from collections import deque

import ChessboardPattern
from Calibration import MonoCameraCalibration, check_chessboard, StereoCameraCalibration
from CalibrationResults import MonoCameraCalibrationResults, StereoCameraCalibrationResults
from CameraProvider import CameraProvider

class Provider(object):
    def __init__(self, camera_indexes, camera_names = None):
        logging.info("Initializing provider for all cameras")

        if camera_names is None:
            camera_names = [None for _ in camera_indexes]

        if len(camera_indexes) != len(camera_names):
            #TODO: should not fail, when missing just some of the names
            raise RuntimeError

        self.camera_names = camera_names
        self.camera_indexes = camera_indexes

        self.images = [deque([], maxlen=500) for _ in camera_indexes]
        self.calibs = []

    def initialize_cameras(self):
            self.camera_providers = []
            for (i, (ind, name)) in enumerate(zip(self.camera_indexes, self.camera_names)):
                self.camera_providers.append(CameraProvider(self.images[i], ind, name))

            [ p.setup_camera(640, 480)  for p in self.camera_providers ]

    def start_capturing(self):
        [ p.start_capturing() for p in self.camera_providers ]

    def stop_capturing(self):
        [ p.stop_capturing() for p in self.camera_providers ]

    def calibrate_cameras(self, use_saved = False):
        if use_saved:
            for _ in self.camera_providers:
                self.calibs.append(MonoCameraCalibration(chessboard_size=ChessboardPattern.chessboard_size ,image_size=(640, 480)))

            self.calibs[0].calibration_results = MonoCameraCalibrationResults(
                camera_matrix = 0,
                distortion_coeffs = 0,
                rotation_vecs = 0,
                translation_vecs = 0
            )

            self.calibs[1].calibration_results = MonoCameraCalibrationResults(
                camera_matrix=0,
                distortion_coeffs=0,
                rotation_vecs=0,
                translation_vecs=0
            )

            return True


        success = True
        if len(self.calibs) != len(self.camera_providers):
            self.calibs = []
            for _ in self.camera_providers:
                self.calibs.append(MonoCameraCalibration(chessboard_size=ChessboardPattern.chessboard_size ,image_size=(640, 480)))

        for cam_ind, calib in enumerate(self.calibs):
            if calib.calibration_results is None:
                minimum = min(len(self.images[cam_ind]), 100)
                images = [self.images[cam_ind][-i] for i in range(minimum)]

                print("Calibrate camera", cam_ind)
                calib_error = self.calibs[cam_ind].calibrate(images)
                logging.info("Calibration end up with {}".format(calib_error))


        uncalibrated = []
        for i, calib in enumerate(self.calibs):
            if calib.calibration_results is None:
                success = False
                uncalibrated.append(i)
            #else:
            #    print(calib.calibration_results)
        print("Cameras", uncalibrated, "not calibrated successfully")

        return success


    def get_times_with_chessboard(self):
        for camera in self.camera_indexes:
            succ = []
            for (time, img) in self.images[camera]:
                ret, _, _ = check_chessboard(img)
                if ret:
                    succ.append(time)
            print(succ)

    def calibrate_pairs(self, use_saved = False): # TODO: for now working with only TWO cameras
        if use_saved:
            self.stereo_calibration.calibration_results = StereoCameraCalibrationResults(
                rotation_matrix = [[ 0.7218315,  -0.18127398,  0.66790646], [ 0.06328574,  0.97833254,  0.1971303 ], [-0.68916922, -0.10002591,  0.7176633 ]],
                translation_matrix = [[-313.31814004],[ -91.22541214],[ 126.20238638]],
                essential_matrix = [[  54.88293477, -114.34299674,  -90.34744443], [-124.83235929,  -54.21714052,  309.1483187 ], [  46.02080661, -323.06612595,   -0.83445697]],
                fundamental_matrix = [[ -1.35848473e-05,   2.82811243e-05,   1.23845886e-02], [  3.06905591e-05,   1.33193765e-05,  -6.31260664e-02], [ -1.39487143e-02,   5.47770955e-02,   1.00000000e+00]],
                reprojection_error = 0.7471242266180657
            )
            return

        print("Pairs")
        assert (len(self.camera_indexes) == 2)

        threshold = 1/10 # TODO: more adequate value

        if len(self.images[0]) < len(self.images[1]):
            smaller = 0
            bigger = 1
        else:
            smaller = 1
            bigger = 0

        j = 0
        images_for_stereo1 = []
        images_for_stereo2 = []

        smallerList = list(self.images[smaller])
        biggerList = list(self.images[bigger])

        for i, (time, image) in enumerate(smallerList):
            ret, corners, gray = check_chessboard(image)
            if ret:
                #najdi adekvatny a aplikuj ich
                while j < len(biggerList) and biggerList[j][0] <= time - threshold:
                    j += 1

                while j < len(biggerList) and biggerList[j][0] <= time + threshold:
                    image2 = biggerList[j][1]
                    ret2, corners, gray = check_chessboard(image2)
                    if ret2:
                        images_for_stereo1.append((time, image))
                        images_for_stereo2.append((biggerList[j][0], image2))

                        print("First {}, second {}".format(time, biggerList[j][0]))
                        break
                    j += 1
        assert(len(images_for_stereo1) == len(images_for_stereo2))

        if len(images_for_stereo1) == 0:
            print("Did not found images for stereo calibration")
            return

        (imgpoint1, objpoints1) = self.calibs[0].find_chessboad(images_for_stereo1, fastCheck=True)
        (imgpoint2, objpoints2) = self.calibs[1].find_chessboad(images_for_stereo2, fastCheck=True)

        print("Initializing stereo calibration")
        self.stereo_calibration = StereoCameraCalibration(self.calibs, imgpoint1, imgpoint2, objpoints1)
        self.stereo_calibration.stereo_calibrate()


        print(self.stereo_calibration.calibration_results)
        print("Stereo calibration finished")

    def get_images_same_time(self):
        pass


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    provider = Provider([2])
    provider.initialize_cameras()
    provider.start_capturing()
    time.sleep(10)
    provider.stop_capturing()

    for i in provider.images:
        print(len(i))
    provider.calibrate_cameras()

#    provider.get_times_with_chessboard()
    provider.calibrate_pairs()
