import random
import cv2
import numpy as np
import Config
from CalibrationResults import MonoCameraCalibrationResults, StereoCameraCalibrationResults


class CalibrationsProvider(object):
    def __init__(self, cameras_provider, stop_event, console_output):
        self.cameras_provider = cameras_provider
        self.image_size = (Config.image_width, Config.image_height)
        self.images = self.cameras_provider.images
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
            saved_results = [None, None]

        for cam_ind in range(Config.camera_count()):
            if saved_results[cam_ind] is not None:
                self.mono_calibration_results[cam_ind] = MonoCameraCalibrationResults(jsonFile=saved_results[cam_ind])
                continue

            if self.mono_calibration_results[cam_ind] is not None:
                continue

            images = self.images[cam_ind]
            images_with_chessboard = self.get_images_with_chessboard(images, self.monocalibration_sample_size)
            if len(images_with_chessboard) < self.minimum_images_for_monocalibration:
                continue
            if len(images_with_chessboard) > self.maximum_images_for_monocalibration:
                images_with_chessboard = random.sample(images_with_chessboard, self.maximum_images_for_monocalibration)

            chessboards = [i.chessboard for i in images_with_chessboard]
            object_points_for_chessboards = [self.object_points_for_chessboard() for _ in
                                             range(len(images_with_chessboard))]

            print("Images used", len(images_with_chessboard))
            self.console_output.append("Starting a calibration of camera " + str(cam_ind + 1) + " on " + str(
                len(images_with_chessboard)) + " images.")
            print("Starting to compute calibration")
            ok, mtx, dist, _, _ = cv2.calibrateCamera(
                objectPoints=object_points_for_chessboards,
                imagePoints=chessboards,
                imageSize=self.image_size,
                cameraMatrix=None,
                distCoeffs=None
            )
            print("Computing finished")
            if ok:
                self.mono_calibration_results[cam_ind] = MonoCameraCalibrationResults(mtx, dist, None, None)
                self.mono_calibration_results[cam_ind].save(cam_ind)
                print("Camera ", cam_ind + 1, " calibrated successfuly")
                self.console_output.append("Camera " + str(cam_ind + 1) + " calibrated successfully.")
            else:
                self.console_output.append(
                    "Camera " + str(cam_ind + 1) + " calibration did not succedeed. Will be repeated.")
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

        self.console_output.append("Looking for images for stereo calibration.")
        import itertools
        images = list(
            itertools.islice(self.find_images_for_stereo_calibration(), self.maximum_images_for_stereocalibration))
        if len(images) < self.minimum_images_for_stereo_calibration:
            self.console_output.append("Not enough images for stereo calibration.")
            return False

        if len(images) > self.maximum_images_for_stereocalibration:
            images = random.sample(images, self.maximum_images_for_stereocalibration)

        self.console_output.append("Computing the stereo calibration from a sample of " + str(len(images)) + " images.")

        imgpoints1 = [i[0].chessboard for i in images]
        imgpoints2 = [i[1].chessboard for i in images]
        objpoints = [self.object_points_for_chessboard() for _ in range(len(imgpoints1))]

        print(len(imgpoints1), "images used for stereo calibration")
        print("Starting to compute stereo calibration")
        rerror, _, _, _, _, r, t, _, _ = \
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
        print("Stereo calibration computed")
        self.stereo_calibration_results = StereoCameraCalibrationResults(r, t, None, None, rerror)
        self.stereo_calibration_results.save()

        self.console_output.append("Stereo calibration finished. Estimated distance between the cameras is " +
                                   str(self.stereo_calibration_results.camera_distance() / 10)
                                   + " centimenters. Reprojection error is " + str(rerror))

        print("Cameras are", self.stereo_calibration_results.camera_distance() / 10,
              "centimenters apart. Reprojection error is", rerror)
        return True

    def get_images_with_chessboard(self, images_queue, maximum):
        found = 0
        images = list(images_queue)
        i = -1
        time_of_last_image = 0
        images_with_chessboard = []
        while not self.stop_event.is_set() and found < maximum:
            i += 1
            if len(images) <= i:
                break
            time, image, chessboard = images[i]
            if time - time_of_last_image < self.skipping_time:
                continue
            if chessboard is False:  # chessboard was not found in previous runs
                continue
            if chessboard is not None:  # chessboard was found in previous runs
                images_with_chessboard.append(images[i])
                time_of_last_image = time
                continue

            chessboard = self.find_chessboard(image)  # run chessboard check

            if chessboard is not None:
                images[i].chessboard = chessboard
                images_with_chessboard.append(images[i])
                time_of_last_image = time
                found += 1
            else:
                images[i].chessboard = False
        return images_with_chessboard

    def find_chessboard(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ok, corners = cv2.findChessboardCorners(
            gray, self.chessboard_inner_corners,
            flags=cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_ADAPTIVE_THRESH)

        inner_corners_count = self.chessboard_inner_corners[0] * self.chessboard_inner_corners[1]
        if ok and len(corners) == inner_corners_count:  # only fully described chessboards are accepted
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (5, 5), (-1, -1), criteria)
            return corners2
        else:
            return None

    def find_images_for_stereo_calibration(self):
        images_iter = []
        for j in range(2):
            while True:
                try:
                    images_i = list(self.images[j])
                except RuntimeError as err:
                    pass
                else:
                    break
            images_iter.append(x for x in images_i if x is not False)

        images = [next(x) for x in images_iter]
        earlier = images[0].time > images[1].time

        last_time = 0

        while True:
            while images[earlier].time <= last_time + self.skipping_time:
                images[earlier] = next(images_iter[earlier])
                earlier = images[0].time > images[1].time
            if images[not earlier].time - images[earlier].time < self.time_threshold:
                for image in images:
                    if image.chessboard is None:
                        image.chessboard = self.find_chessboard(image.image)
                        if image.chessboard is None:
                            image.chessboard = False
                            break
                if all((x.chessboard is not False and x.chessboard is not None) for x in images):
                    yield images[0], images[1]
                last_time = images[not earlier].time
            images[earlier] = next(images_iter[earlier])
            earlier = images[0].time > images[1].time