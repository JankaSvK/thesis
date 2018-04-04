from optparse import OptionParser

options_calib1 = "calibration_results1"
options_calib2 = "calibration_results2"
options_stereo = "stereo_calibration_results"
options_video1 = "video_recording1"
options_video2 = "video_recording2"

def parse_options():
    parser = OptionParser()


    # Mono calibration results as an input
    parser.add_option("--calibration_results1", dest=options_calib1,
                      help="Calibration results for the first camera", metavar="CALIB1")
    parser.add_option("--calibration_results2", dest=options_calib2,
                      help="Calibration results for the second camera", metavar="CALIB2")

    # Stereo calibration result as an input
    parser.add_option("--stereo_calibration_results", dest=options_stereo,
                      help="Stereo calibration results", metavar="STEREO")

    # Video recordings on input
    parser.add_option("--video_recording1", dest=options_video1,
                      help="Video recording for the first camera", metavar="VIDEO1")
    parser.add_option("--video_recording2", dest=options_video2,
                      help="Video recording for the second camera", metavar="VIDEO2")

    (options, args) = parser.parse_args()

    return options