import logging
from collections import deque

import time

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

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    provider = Provider([1])
    provider.initialize_cameras()
    provider.start_capturing()
    time.sleep(5)
    provider.stop_capturing()

    for i in provider.images:
        print(len(i))