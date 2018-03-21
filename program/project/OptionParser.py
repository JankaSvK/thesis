from optparse import OptionParser

parser = OptionParser()

# Mono calibration results as an input
parser.add_option("--calibration_results1", dest="calibration_results1",
                  help="Calibration results for the first camera", metavar="CALIB1")
parser.add_option("--calibration_results2", dest="calibration_results2",
                  help="Calibration results for the second camera", metavar="CALIB2")

# Stereo calibration result as an input
parser.add_option("--stereo_calibration_results", dest="stereo_calibration_results",
                  help="Stereo_calibration_results", metavar="STEREO")

# Video recordings on input
parser.add_option("--video_recording1", dest="video_recording1",
                  help="video_recording1 for the first camera", metavar="VIDEO1")
parser.add_option("--video_recording2", dest="video_recording2",
                  help="video_recording2 for the second camera", metavar="VIDEO2")

(options, args) = parser.parse_args()

