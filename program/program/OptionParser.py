from optparse import OptionParser

def parse_options():
    parser = OptionParser()

    # Setting cameras
    parser.add_option("--camera_input1", dest="camera1",
                      help="Index of camera to be run as left camera", metavar="NUMBER")
    parser.add_option("--camera_input2", dest="camera2",
                      help="Index of camera to be run as left camera", metavar="NUMBER")

    # Defining how many objects will be tracked
    parser.add_option("-o", "--number_of_objects", dest="objects_count", type="int",
                      help="Number of objects to be tracked.", metavar="NUMBER")

    # Mono calibration results as an input
    parser.add_option("--calibration_results1", dest="calibration_results1",
                      help="Calibration results for the first camera", metavar="FILE")
    parser.add_option("--calibration_results2", dest="calibration_results2",
                      help="Calibration results for the second camera", metavar="FILE")

    # Stereo calibration result as an input
    parser.add_option("--stereo_calibration_results", dest="stereo_calibration_results",
                      help="Stereo calibration results", metavar="FILE")

    # Video recordings on input
    parser.add_option("--video1", dest="video1",
                      help="Video recording for the first camera", metavar="FILE")
    parser.add_option("--video2", dest="video2",
                      help="Video recording for the second camera", metavar="FILE")

    # Tracker
    parser.add_option("-t", "--tracker", dest="tracker",
                      help="The algorithm used for tracking", metavar="TRACKER")

    parser.add_option("--chessboard", dest="chessboard",
                      help="Calibration chessboard parameters (inner_cornersX,inner_cornersY,size)", metavar="TRIPLE")

    parser.add_option("--bbox", dest="bbox",
                      help="Bounding boxes")

    (options, args) = parser.parse_args()

    return options