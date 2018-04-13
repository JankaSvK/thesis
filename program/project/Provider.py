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

    def initialize_cameras(self, video_recordings = None):
            if video_recordings is None:
                video_recordings = [None, None]

            self.camera_providers = []
            for (i, (ind, name)) in enumerate(zip(self.camera_indexes, self.camera_names)):
                self.camera_providers.append(CameraProvider(self.images[i], ind, name, video_recording=video_recordings[i]))

            [ p.setup_camera(640, 480)  for p in self.camera_providers ]

            self.calibs = [
                MonoCameraCalibration(chessboard_size=ChessboardPattern.chessboard_size, image_size=(640, 480)) for _ in self.camera_providers
            ]

    def start_capturing(self):
        [ p.start_capturing() for p in self.camera_providers ]

    def stop_capturing(self):
        [ p.stop_capturing() for p in self.camera_providers ]

    def calibrate_cameras(self, use_saved = []):
        if use_saved == []:
            use_saved = [None, None]

        for cam_ind, calib in enumerate(self.calibs):
            if use_saved[cam_ind] is not None:
                self.calibs[cam_ind].calibration_results = MonoCameraCalibrationResults(jsonFile=use_saved[cam_ind])
            elif calib.calibration_results is None:
                minimum = min(len(self.images[cam_ind]), 100)
                images = [self.images[cam_ind][-i] for i in range(minimum)]

 #               print("Calibrate camera", cam_ind)
                calib_error = self.calibs[cam_ind].calibrate(images)
                logging.info("Calibration end up with {}".format(calib_error))
                if calib_error is not False:
                    print("Camera", cam_ind, "calibrated successfuly")


        uncalibrated = []
        for i, calib in enumerate(self.calibs):
            if calib.calibration_results is None:
                uncalibrated.append(i)
#        print("Cameras", uncalibrated, "not calibrated successfully")

        if uncalibrated == []:
            for i, calib in enumerate(self.calibs):
                if use_saved[i] is None:
                    calib.calibration_results.save(i)

        return (uncalibrated == [])

    def get_times_with_chessboard(self):
        for camera in self.camera_indexes:
            succ = []
            for (time, img) in self.images[camera]:
                ret, _, _ = check_chessboard(img)
                if ret:
                    succ.append(time)
            print(succ)

    def calibrate_pairs(self, use_saved = None): # TODO: for now working with only TWO cameras
        if use_saved is not None:
            print("Using saved data for stereo calibration.")
            self.stereo_calibration = StereoCameraCalibration(jsonFile = use_saved)
            return True

        print("Starting stereo calibration")
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
                while j < len(biggerList) and biggerList[j][0] <= time - threshold:
                    j += 1

                while j < len(biggerList) and biggerList[j][0] <= time + threshold:
                    image2 = biggerList[j][1]
                    ret2, corners, gray = check_chessboard(image2)
                    if ret2:
                        images_for_stereo1.append((time, image))
                        images_for_stereo2.append((biggerList[j][0], image2))

#                        print("First {}, second {}".format(time, biggerList[j][0]))
                        j += 1
                        break
                    j += 1
        assert(len(images_for_stereo1) == len(images_for_stereo2))

        if len(images_for_stereo1) < 5:
            print("Did not found images for stereo calibration")
            return False

        print("For stereo calibration available ", len(images_for_stereo1), "images.")
        consider = 40
        print("Considering ", consider, "images.")
        images_for_stereo1 = images_for_stereo1[:consider]
        images_for_stereo2 = images_for_stereo2[:consider]

        (imgpoint1, objpoints1) = self.calibs[0].find_chessboad(images_for_stereo1, fastCheck=True)
        (imgpoint2, objpoints2) = self.calibs[1].find_chessboad(images_for_stereo2, fastCheck=True)

        print("Initializing stereo calibration")
        self.stereo_calibration = StereoCameraCalibration(self.calibs, imgpoint1, imgpoint2, objpoints1)
        self.stereo_calibration.stereo_calibrate()

        self.stereo_calibration.calibration_results.save()
        #print(self.stereo_calibration.calibration_results)
        print("Stereo calibration finished")
        print("Cameras are", self.stereo_calibration.calibration_results.camera_distance() / 10, "centimenters apart.")
        return True
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
