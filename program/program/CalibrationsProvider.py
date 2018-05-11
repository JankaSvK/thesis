import random
import itertools
import cv2
import numpy as np
from . import Config
from .CalibrationResults import MonoCameraCalibrationResults, StereoCameraCalibrationResults


class CalibrationsProvider(object):
    def __init__(self, cameras_provider, stop_event, console_output):
        self.cameras_provider = cameras_provider
        self.image_size = (Config.image_width, Config.image_height)
        self.image_entries = self.cameras_provider.image_entries
        self.stop_event = stop_event
        self.console_output = console_output

        self.chessboard_inner_corners = Config.chessboard_inner_corners
        self.chessboard_square_size = Config.chessboard_square_size

        self.mono_calibration_results = [None, None]
        self.stereo_calibration_results = None
        self.object_points = None

        # Calibration parameters setting
        self.minimum_images_for_monocalibration = Config.minimum_images_for_monocalibration
        self.maximum_images_for_monocalibration = Config.maximum_images_for_monocalibration
        self.minimum_images_for_stereo_calibration = Config.minimum_images_for_stereocalibration
        self.maximum_images_for_stereocalibration = Config.maximum_images_for_stereocalibration
        self.monocalibration_sample_size = Config.maximum_images_for_monocalibration_sampling
        self.stereocalibration_sample_size = Config.maximum_images_for_stereocalibration_sampling
        self.time_threshold = Config.time_threshold_for_correspondence
        self.skipping_time = Config.skipping_time

    def mono_calibrate(self, saved_results=None):
        if saved_results is None:
            saved_results = [None for _ in Config.camera_count]

        for cam_ind in range(Config.camera_count):
            if saved_results[cam_ind] is not None:
                self.mono_calibration_results[cam_ind] = MonoCameraCalibrationResults(jsonFile=saved_results[cam_ind])
                continue

            if self.mono_calibration_results[cam_ind] is not None:
                continue

            images = self.image_entries[cam_ind]
            images_with_chessboard = self.sample_calibration_images(self.get_images_with_chessboard(images),
                                                                    self.minimum_images_for_monocalibration,
                                                                    self.maximum_images_for_monocalibration,
                                                                    self.monocalibration_sample_size)
            if images_with_chessboard is None:
                continue

            chessboards = [i.get_chessboard() for i in images_with_chessboard]
            object_points_for_chessboards = [self.object_points_for_chessboard() for _ in
                                             range(len(images_with_chessboard))]

            self.console_output.append(
                "Starting a calibration of camera {} on {} images.".format(cam_ind + 1, len(images_with_chessboard)))
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
        if saved_results is not None:
            self.stereo_calibration_results = StereoCameraCalibrationResults(jsonFile=saved_results)
            return True

        if self.stereo_calibration_results is not None:
            return True

        images = self.sample_calibration_images(self.find_images_for_stereo_calibration(),
                                                self.minimum_images_for_stereo_calibration,
                                                self.maximum_images_for_stereocalibration,
                                                self.stereocalibration_sample_size)
        if images is None:
            return False

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

    def sample_calibration_images(self, image_iterator, minimum, maximum, sample_size):
        images = list(itertools.islice(image_iterator, sample_size))
        if len(images) < minimum:
            return None
        if len(images) > maximum:
            return random.sample(images, maximum)
        return images

    def get_images_with_chessboard(self, images_queue):
        images = iter(self.threadsafe_list_copy(images_queue))
        time_of_last_image = 0
        while not self.stop_event.is_set():
            image_entry = next(images)
            if image_entry.timestamp - time_of_last_image < self.skipping_time:
                continue
            if not image_entry.chessboard_checked():
                image_entry.add_chessboard(self.find_chessboard(image_entry.image))
            if image_entry.contains_chessboard():
                yield image_entry
                time_of_last_image = image_entry.timestamp
        raise StopIteration

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

    def find_images_for_stereo_calibration(self):
        def may_contain_chessboard(image):
            return not image.chessboard_checked() or image.contains_chessboard()

        images_iter = [filter(may_contain_chessboard, self.threadsafe_list_copy(image_entries)) for image_entries in self.image_entries]
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