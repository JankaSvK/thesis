import logging
import time
from collections import deque

import ChessboardPattern
from Calibration import MonoCameraCalibration, check_chessboard, StereoCameraCalibration
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

    def calibrate_cameras(self):
        for camera in self.camera_indexes: # TODO: should be done in parallel way
            self.calibs.append(MonoCameraCalibration(chessboard_size=ChessboardPattern.chessboard_size ,image_size=(640, 480)))
            minimum = min(len(self.images[camera]), 200)
            images = [self.images[camera][i] for i in range(minimum)]
            error = self.calibs[-1].calibrate(images)
            logging.info("Calibration end up with {}".format(error))

    def get_times_with_chessboard(self):
        for camera in self.camera_indexes:
            succ = []
            for (time, img) in self.images[camera]:
                ret, _, _ = check_chessboard(img)
                if ret:
                    succ.append(time)
            print(succ)

    def calibrate_pairs(self): # TODO: for now working with only TWO cameras
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
        for i, (time, image) in enumerate(self.images[smaller]):
            ret, corners, gray = check_chessboard(image)
            if ret:
                #najdi adekvatny a aplikuj ich
                while self.images[bigger][j][0] <= time - threshold:
                    j += 1

                while self.images[bigger][j][0] <= time + threshold:
                    image2 = self.images[bigger][j][1]
                    ret2, corners, gray = check_chessboard(image2)
                    if ret2:
                        images_for_stereo1.append(image)
                        images_for_stereo2.append(image2)

                        print("First {}, second {}".format(time, self.images[bigger][j][0]))
                        break
                    j += 1
        assert(len(images_for_stereo1) == len(images_for_stereo2))

        #(imgpoint1, objpoints1) = self.calibs[0].find_chessboad(images_for_stereo1)
        #(imgpoint2, objpoints2) = self.calibs[1].find_chessboad(images_for_stereo2)

        print("Initializing stereo calibration")
        #self.stereo_calibration = StereoCameraCalibration(self.calibs, imgpoint1, imgpoint2, objpoints1)
        #self.stereo_calibration.stereo_calibrate()

        print("Stereo calibration finished")

    def get_images_same_time(self):
        pass


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    provider = Provider([0, 1])
    provider.initialize_cameras()
    provider.start_capturing()
    time.sleep(10)
    provider.stop_capturing()

    for i in provider.images:
        print(len(i))
    provider.calibrate_cameras()

#    provider.get_times_with_chessboard()
    provider.calibrate_pairs()
