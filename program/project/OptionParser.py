from optparse import OptionParser

def parse_options():
    parser = OptionParser()


    # Setting cameras
    parser.add_option("--camera_input1", dest="camera1",
                      help="Index of camera to be run as left camera", metavar="NUMBER")
    parser.add_option("--camera_input2", dest="camera2",
                      help="Index of camera to be run as left camera", metavar="NUMBER")

    # Mono calibration results as an input
    parser.add_option("--calibration_results1", dest="calibration_results1",
                      help="Calibration results for the first camera", metavar="FILE")
    parser.add_option("--calibration_results2", dest="calibration_results2",
                      help="Calibration results for the second camera", metavar="FILE")

    # Stereo calibration result as an input
    parser.add_option("--stereo_calibration_results", dest="stereo_calibration_results",
                      help="Stereo calibration results", metavar="FILE")

    # Video recordings on input
    parser.add_option("--video_recording1", dest="video_recording1",
                      help="Video recording for the first camera", metavar="FILE")
    parser.add_option("--video_recording2", dest="video_recording2",
                      help="Video recording for the second camera", metavar="FILE")

    # Tracker
    parser.add_option("--tracker", dest="tracker",
                      help="The algorithm used for tracking", metavar="TRACKER")

    (options, args) = parser.parse_args()

    return options