import cv2


class TrackerFactory(object):
    @classmethod
    def get_tracker(cls, tracker_type):
        if tracker_type == 'MIL':
            return cv2.TrackerMIL_create()
        if tracker_type == 'BOOSTING':
            return cv2.TrackerBoosting_create()
        if tracker_type == 'TLD':
            return cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            return cv2.TrackerMedianFlow_create()
        if tracker_type == 'SIMPLEBACKGROUND':
            from .trackers.TrackerSimpleBackground import TrackerSimpleBackground
            return TrackerSimpleBackground()
        if tracker_type == 'HSV':
            from .trackers.TrackerHSV import TrackerHSV
            return TrackerHSV()
        if tracker_type == 'PATTERNMATCHING':
            from .trackers.TrackerPatternMatching import TrackerPatternMatching
            return TrackerPatternMatching()
        if tracker_type == 'CORRELATION':
            from .trackers.TrackerCorrelation import CorrelationTracker
            return CorrelationTracker()
        if tracker_type == 'MOSSE':
            return cv2.TrackerMOSSE_create()
        if tracker_type == 'EXPERIMENTS':
            from .trackers.TrackerExperiments import TrackerExperiments
            return TrackerExperiments()
        else:
            print("Default tracker will be used")
            return cv2.TrackerKCF_create()
