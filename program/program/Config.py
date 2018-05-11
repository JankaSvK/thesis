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

def camera_count():
    return len(camera_initialize)

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
initial_bounding_boxes = [[[132, 56], [130, 157], [331, 103], [315, 207]], [[133, 53], [135, 194], [426, 64], [404, 196]]]

### Calibration settings

# Minimum numbers of images for mono calibration.
# Can not be less than 3
minimum_images_for_monocalibration = 15

# Maximum number of images for stereo calibration. If more has been found, a sample set of them is taken.
maximum_images_for_monocalibration = 30

# A size of sampling set. Bigger takes more time to find, but provides higher variation to the images.
maximum_images_for_monocalibration_sampling = 2 * maximum_images_for_monocalibration

# Minimum number of the images for stereo calibration
minimum_images_for_stereocalibration = 10

# Maximum number of the images for stereo calibration. If more exists, a sample set of them is taken.
maximum_images_for_stereocalibration = 50

# A size of the sampling set. Bigger takes more time to find, but provides higher variation to the images.
maximum_images_for_stereocalibration_sampling = 3 * maximum_images_for_stereocalibration

# Stereo calibration considers images as corresponding if their time do not differ more than this threshold.
time_threshold_for_correspondence = 1/20

# Seconds to skip between the images used for calibration (mono and stereo).
# Reason: Similar images provides "same" information.
skipping_time = 0.2
