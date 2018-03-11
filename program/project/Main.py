import threading
import logging
from collections import Set
from queue import Queue
from ComplexTracker import ComplexTracker
import cv2

from GUI import GUI
from Provider import Provider

def clickCounter(queue, number_of_cameras, image_streams, output_streams):
    bboxes = []
    trackers = []

    for i in range(number_of_cameras):
        bboxes.append([])
        trackers.append(ComplexTracker(i,image_stream=image_streams[i], output_stream=output_streams[i]))

    bboxes_created = set()

    while len(bboxes_created) != number_of_cameras:
        (id, x, y) = queue.get()
        if len(bboxes[id]) < 2:
            bboxes[id].append((x, y))
        if len(bboxes[id]) == 2:
            bboxes_created.add(id)
            trackers[id].set_initial_position(bboxes[id][0], bboxes[id][1])
            trackers[id].start_tracking()

            # start tracking
    print("Got all bounding box")

    return (bboxes, trackers)
#logging.getLogger().setLevel(logging.INFO)

provider = Provider([0, 1])
provider.initialize_cameras()
provider.start_capturing()

gui_actions_queue = Queue()
gui = GUI(gui_actions_queue)
guiThread = threading.Thread(target=gui.start, args=(provider.images,), name="GUI")
guiThread.start()

#while not provider.calibrate_cameras():
    #print("New calibration")
#    pass

#print("!!! Cameras calibrated")


#provider.calibrate_pairs()

#### One small step further

coords = []
for i in range(2):
    coords.append([])
bboxes = clickCounter(gui_actions_queue, 2, provider.images, coords)

print("Got here")

while True:
    print(coords[0][-1])
#Draw them

#while True:
#    if not gui_actions_queue.empty():
#        print(gui_actions_queue.get())


# Initializing tracking on both cameras
#click on both twice





#
# # Getting projection matrices
#
# firstCameraResults = provider.calibs[0].calibration_results
# secondCameraResults = provider.calibs[1].calibration_results
# stereoResults = provider.stereo_calibration.calibration_results
#
# RL, RR, PL, PR, _, _, _ = cv2.stereoRectify(
#     firstCameraResults.camera_matrix, firstCameraResults.distortion_coeffs,
#     secondCameraResults.camera_matrix, secondCameraResults.distortion_coeffs,
#     (640, 480), stereoResults.rotation_matrix, stereoResults.translation_matrix, alpha=0)
#
# # Getting points
#
#
# locatedPoints = cv2.triangulatePoints(PL, PR, [], []) #TODO add coordinates