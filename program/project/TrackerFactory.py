import cv2

from trackers.TrackerPatternMatching import TrackerPatternMatching
from trackers.TrackerSimpleBackground import TrackerSimpleBackground
from trackers.TrackerHSV import TrackerHSV
from trackers.TrackerCorrelation import CorrelationTracker


class TrackerFactory(object):

    @classmethod
    def get_tracker(cls, tracker_type):
        return {
            'KCF': cv2.TrackerKCF_create(),
            'MIL': cv2.TrackerMIL_create(),
            'BOOSTING': cv2.TrackerBoosting_create(),
            'TLD': cv2.TrackerTLD_create(),
            'MEDIANFLOW': cv2.TrackerMedianFlow_create(),
#            'GOTURN': cv2.TrackerGOTURN_create(),
            'SIMPLEBACKGROUND': TrackerSimpleBackground(),
            'HSV': TrackerHSV(),
            'PATTERNMATCHING': TrackerPatternMatching(),
            'CORRELATION': CorrelationTracker()
        }.get(tracker_type, cv2.TrackerKCF_create())