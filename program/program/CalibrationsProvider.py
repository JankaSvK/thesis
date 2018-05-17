import cv2
import numpy as np

from program.QueueIterator import QueueIteratorManager, QueueIterator
from . import Config
from .CalibrationResults import MonoCameraCalibrationResults, StereoCameraCalibrationResults, CalibrationImportError


class UnsuccessfulCalibration(Exception):
    pass


class CalibrationsProvider(object):
    def __init__(self, cameras_provider, stop_event, console_output, input_end):
        self.cameras_provider = cameras_provider
        self.image_size = (Config.image_width, Config.image_height)
        self.image_entries = self.cameras_provider.image_entries
        self.stop_event = stop_event
        self.console_output = console_output
        self.input_ended = input_end

        self.chessboard_inner_corners = Config.chessboard_inner_corners
        self.chessboard_square_size = Config.chessboard_square_size

        self.mono_calibration_results = [None, None]
        self.stereo_calibration_results = None
        self.object_points = None

        # Calibration parameters setting
        self.monocalibration_sample_size = Config.images_for_monocalibration_sampling
        self.stereocalibration_sample_size = Config.images_for_stereocalibration_sampling
        self.time_threshold = Config.time_threshold_for_correspondence
        self.skipping_time = Config.skipping_time

    def mono_calibrate(self, saved_results=None):
        if saved_results is None:
            saved_results = [None for _ in Config.camera_count]

        to_calibrate = {i for i in range(Config.camera_count)}

        for cam_ind, result in enumerate(saved_results):
            if result is not None:
                try:
                    self.mono_calibration_results[cam_ind] = MonoCameraCalibrationResults(json_file=result)
                except CalibrationImportError:
                    self.console_output.append(
                        "ERR: Importing saved calibration data for camera {} failed.".format(cam_ind))

            if self.mono_calibration_results[cam_ind] is not None:
                to_calibrate.discard(cam_ind)

        if to_calibrate:
            self.console_output.append("Starting calibration process. Move with the chessboard in camera view...")
        queues = {i: QueueIterator(queue, self.input_ended) for i, queue in enumerate(self.image_entries) if
                  i in to_calibrate}
        images_with_chessboard_per_camera = self.get_images_with_chessboard(queues, self.monocalibration_sample_size)
        for cam_ind in to_calibrate:
            images_with_chessboard = images_with_chessboard_per_camera[cam_ind]
            chessboards = [i.get_chessboard() for i in images_with_chessboard]
            object_points_for_chessboards = [self.object_points_for_chessboard() for _ in
                                             range(len(images_with_chessboard))]
            self.console_output.append(
                "Starting a calibration of camera {} on {} images.".format(cam_ind + 1, len(images_with_chessboard)))

            if self.stop_event.is_set():
                return
            ok, mtx, dist, _, _ = cv2.calibrateCamera(
                objectPoints=object_points_for_chessboards,
                imagePoints=chessboards,
                imageSize=self.image_size,
                cameraMatrix=None,
                distCoeffs=None
            )
            if ok:
                self.mono_calibration_results[cam_ind] = MonoCameraCalibrationResults(mtx, dist, None, None)
                self.mono_calibration_results[cam_ind].save(cam_ind)
                self.console_output.append("Camera {} calibrated successfully.".format(cam_ind + 1))
            else:
                self.console_output.append(
                    "Camera {} calibration did not succedeed. Will be repeated.".format(cam_ind + 1))
        return all(x is not None for x in self.mono_calibration_results)

    def object_points_for_chessboard(self):
        if self.object_points is None:
            objp = np.zeros((self.chessboard_inner_corners[0] * self.chessboard_inner_corners[1], 3), np.float32)
            objp[:, :2] = np.mgrid[0:self.chessboard_inner_corners[0],
                          0:self.chessboard_inner_corners[1]].T.reshape(-1, 2) * self.chessboard_square_size
            self.object_points = objp
        return self.object_points

    def stereo_calibrate(self, saved_results=None):
        successful_import = None
        if saved_results is not None:
            try:
                self.stereo_calibration_results = StereoCameraCalibrationResults(json_file=saved_results)
                successful_import = True
            except CalibrationImportError:
                successful_import = False
                self.console_output.append("ERR: Importing saved calibration data for stereo calibration failed.")

        if successful_import:
            return True

        if self.stereo_calibration_results is not None:
            return True
        self.console_output.append(
            "Starting stereo calibration. Please move wtih a chessboard, but keep it visicble in both cameras...")
        images = self.find_images_for_stereo_calibration(self.stereocalibration_sample_size)
        self.console_output.append("Computing the stereo calibration from a sample of {} images.".format(len(images)))

        imgpoints1 = [i[0].get_chessboard() for i in images]
        imgpoints2 = [i[1].get_chessboard() for i in images]
        objpoints = [self.object_points_for_chessboard() for _ in imgpoints1]

        rerror, _, _, _, _, r, t, e, f = \
            cv2.stereoCalibrate(objectPoints=objpoints,
                                imagePoints1=imgpoints1,
                                imagePoints2=imgpoints2,
                                cameraMatrix1=self.mono_calibration_results[0].camera_matrix,
                                distCoeffs1=self.mono_calibration_results[0].distortion_coeffs,
                                cameraMatrix2=self.mono_calibration_results[1].camera_matrix,
                                distCoeffs2=self.mono_calibration_results[1].distortion_coeffs,
                                imageSize=(1, 1),
                                criteria=(cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-4)
                                )
        self.stereo_calibration_results = StereoCameraCalibrationResults(r, t, e, f, rerror)
        self.stereo_calibration_results.save()

        self.console_output.append("Stereo calibration finished. Estimated distance between the cameras is {} "
                                   "centimenters. Reprojection error is {}.".format(
            self.stereo_calibration_results.camera_distance() / 10, rerror))

        return True

    def get_images_with_chessboard(self, images_queues, sample_size):
        last_times = {k: -1 for k in images_queues.keys()}
        samples = {k: [] for k in images_queues.keys()}

        while not self.stop_event.is_set() and images_queues:
            try:
                image_entries = {k: next(im) for k, im in images_queues.items()}
            except StopIteration:
                raise UnsuccessfulCalibration
            for i, entry in image_entries.items():
                if entry.timestamp - last_times[i] < self.skipping_time:
                    continue
                if not entry.chessboard_checked():
                    entry.add_chessboard(self.find_chessboard(entry.image))
                if entry.contains_chessboard():
                    samples[i].append(entry)
                    last_times[i] = entry.timestamp
                    if len(samples[i]) == sample_size:
                        del images_queues[i]
                    self.console_output.append(
                        "  {} / {} Images gathered for monocalibration #{}".format(len(samples[i]), sample_size, i + 1))
        return samples

    def find_chessboard(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ok, corners = cv2.findChessboardCorners(
            gray, self.chessboard_inner_corners,
            flags=cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_ADAPTIVE_THRESH)

        inner_corners_count = self.chessboard_inner_corners[0] * self.chessboard_inner_corners[1]

        if not ok or len(corners) != inner_corners_count:  # only fully described chessboards are accepted
            return None

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        return cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)

    def threadsafe_list_copy(self, iterable):
        while True:
            try:
                res = list(iterable)
            except RuntimeError:
                pass
            else:
                return res

    def find_images_for_stereo_calibration(self, sample_size):
        def may_contain_chessboard(image):
            return not image.chessboard_checked() or image.contains_chessboard()

        def iter_over_images():
            manager = QueueIteratorManager(self.image_entries, self.input_ended)
            images_iter = manager.queue_iters
            images = [next(x) for x in images_iter]
            earlier = images[0].timestamp > images[1].timestamp
            last_time = 0

            while not self.stop_event.is_set():
                while images[earlier].timestamp <= last_time + self.skipping_time:
                    images[earlier] = next(images_iter[earlier])
                    earlier = images[0].timestamp > images[1].timestamp
                if images[not earlier].timestamp - images[earlier].timestamp < self.time_threshold:
                    for image in images:
                        if not image.chessboard_checked():
                            image.add_chessboard(self.find_chessboard(image.image))
                    if all(x.contains_chessboard() for x in images):
                        yield images[0], images[1]
                    last_time = images[not earlier].timestamp
                images[earlier] = next(images_iter[earlier])
                earlier = images[0].timestamp > images[1].timestamp
            raise StopIteration

        result = []
        iterator = iter_over_images()
        for i in range(sample_size):
            try:
                result.append(next(iterator))
            except StopIteration:
                raise UnsuccessfulCalibration
            self.console_output.append("  {} / {} Images gathered for stereocalibration".format(i + 1, sample_size))
        return result
