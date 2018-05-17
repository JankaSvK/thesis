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
initial_bounding_boxes = None

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


#### Memory ####
# Since in 32bit system less memory is available, it might not be possible to save 2 * 500 snapshots.
# We introduce two variables to set the default number of saved images per camera based on architecture
images32bit = 200
images64bit = 500
