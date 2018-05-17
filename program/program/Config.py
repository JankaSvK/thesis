### Configuration file
# This configuration contains more advanced configuration settings.
# If you want to change the port that camera initialize, provide video input instead of cameras, use saved calibration
# data or change number of tracked object, please pass it as an option to the application. For more information use --help.

# Number of chessboard inner corners. The order does not matter. May be changed by option provided to the script.
chessboard_inner_corners = (7, 8)
# Length of the square side in millimeters. It has to be square (not rectangle). May be changed by option provided to the script.
chessboard_square_size = 22

# Camera indeces to ititialize cameras. May be changed by option provided to the script.
camera_initialize = [0, 1]
camera_count = len(camera_initialize)

# def camera_count():
#    return len(camera_initialize)

# Count of the objects to be tracked. May be changed by option provided to the script.
objects_count = 1

# Size of the images. Other values not tested, since trackers are already slow and in smaller images only big objects may be tracked.
image_width = 640
image_height = 480

# If it is None, the trackers will wait for interaction.
# Otherwise it can be setted to a list of bouding boxes - Bounding_boxes[camera_index][object_index]
# Therefore it should contains 2 * objects_count entries
# Bouding box is a [x, y, width, height]
# Sample value for two objects: [[[0, 0, 1, 1], [150, 100, 100, 100]], [[100, 100, 50, 50], [200, 200, 20, 20]]]
initial_bounding_boxes = [[[296, 99], [270, 118], [237, 138], [199, 168], [146, 200], [82, 244], [0, 301], [412, 126], [398, 147], [378, 175], [354, 208], [321, 249], [279, 304], [220, 381], [132, 56], [130, 157], [331, 103], [315, 207]], [[155, 59], [155, 90], [146, 125], [147, 173], [138, 233], [132, 309], [124, 418], [318, 66], [333, 95], [347, 132], [370, 176], [396, 232], [431, 306], [481, 411], [133, 53], [135, 194], [426, 64], [404, 196]]]

### Calibration settings

# number of images required for mono calibration - per each camera
images_for_monocalibration_sampling = 20

# Number of images required for stereo calibration
images_for_stereocalibration_sampling = 12

# Stereo calibration considers images as corresponding if their time do not differ more than this threshold.
time_threshold_for_correspondence = 1 / 20

# Seconds to skip between the images used for calibration (mono and stereo).
# Reason: Similar images provides "same" information.
skipping_time = 0.2
