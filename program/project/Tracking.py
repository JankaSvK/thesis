import Config
from QueuesProvider import QueuesProvider
from ComplexTracker import ComplexTracker

class Tracking(object):
    def __init__(self, tracker_type, stop_event):
        self.stop_event = stop_event
        self.tracker_type = tracker_type
        self.trackers = [ComplexTracker(i, QueuesProvider.Images[i], QueuesProvider.TrackedPoints2D[i], tracker_type=tracker_type) for i in Config.camera_indexes]
        self.not_initialized_cameras = list(Config.camera_indexes) # to create new instance

    def start_tracker(self, i, bbox):
        self.trackers[i].set_initial_position(bbox[0], bbox[1])
        self.trackers[i].start_tracking(self.stop_event)

    def wait_until_all_trackers_initialized(self):
        while not self.stop_event.is_set() and self.not_initialized_cameras != []:
            for cam_ind in self.not_initialized_cameras:
                if(len(QueuesProvider.MouseClicks[cam_ind])) >= 2:
                    bbox = QueuesProvider.MouseClicks[cam_ind][-2:]
                    self.start_tracker(cam_ind, bbox)
                    self.not_initialized_cameras.remove(cam_ind)

    def reinitialize_tracker(self, index):
        border = len(QueuesProvider.TrackedPoints2D[index])
        old_tracker = self.trackers[index]
        self.trackers[index] = ComplexTracker(index, QueuesProvider[index], QueuesProvider.TrackedPoints2D[index], tracker_type=self.tracker_type)
        while not self.stop_event.is_set and len(QueuesProvider.TrackedPoints2D[index]) - border < 2:
            pass
        bbox = QueuesProvider.MouseClicks[index][-2:]

        old_tracker.stop_tracking()
        self.start_tracker(index, bbox)