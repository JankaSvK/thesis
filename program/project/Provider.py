import logging
import time
from collections import deque

import ChessboardPattern
from Calibration import MonoCameraCalibration
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
        for camera in self.camera_indexes:
            # mas images pre kazdu kameru
            calib = MonoCameraCalibration(chessboard_size=ChessboardPattern.chessboard_size ,image_size=(640, 480))
            minimum = min(len(self.images[camera]), 50)
            images = [self.images[camera][i] for i in range(minimum)]
            print(len(images))
            error = calib.calibrate(images) # malo by ist viac sucasne aby sa necakalo
            logging.info("Calibration end up with {}".format(error))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    provider = Provider([0])
    provider.initialize_cameras()
    provider.start_capturing()
    time.sleep(5)
    provider.stop_capturing()

    for i in provider.images:
        print(len(i))
    provider.calibrate_cameras()
