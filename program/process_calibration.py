from two_camera_calibration import *
from camera_input import *

cameras = [1,2]
images = [deque([], maxlen=500) for camera in cameras]

wrappers = []
for i, camera in enumerate(cameras):
    wrappers.append(CameraWrapper(camera, images[i]))
    wrappers[i].start_camera()

time.sleep(3)

cams = []
for i,camera in enumerate(cameras):
    print(len(images[0]))
    cams.append(MonoCameraCalibration(wrappers[0].get_images(15)))
    cams[i].find_chessboad()
    cams[i].calibrate()
    print("Camera with index ", camera, " ", cams[i].successful, "calibrated. ", "Error is", cams[i].compute_error())


print("Stopping cameras")
for wrap in wrappers:
    wrap.stop_capturing()

