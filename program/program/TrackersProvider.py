import time
from threading import Thread

from . import Config
from .QueuesEntries import Point
from .TrackerFactory import TrackerFactory


def get_tracker_uid(cam_ind, obj_ind):
    return cam_ind * Config.objects_count + obj_ind


def get_tracker_by_uid(uid):
    return (int(uid / Config.objects_count), int(uid % Config.objects_count))


class TrackersProvider(object):
    def __init__(self, images1, images2, mouse_clicks, coordinates, stop_event, initialization_events, console_output,
                 tracker_type='KCF', number_of_tracked_objects=1):
        self.image_entries = [images1, images2]
        self.object_count = number_of_tracked_objects
        self.tracker_type = tracker_type
        self.mouse_clicks = mouse_clicks
        self.initialization_events = initialization_events
        self.coordinates = coordinates
        self.stop_event = stop_event
        self.console_output = console_output

        self.trackers = []
        for cam_ind, image_stream in enumerate(self.image_entries):
            for obj_ind in range(self.object_count):
                uid = get_tracker_uid(cam_ind, obj_ind)
                self.trackers.append(
                    Tracker(cam_ind=cam_ind, obj_ind=obj_ind,
                            tracker_type=tracker_type,
                            image_stream=image_stream,
                            coordinates=self.coordinates[uid],
                            initialization_event=self.initialization_events[uid],
                            console_output=console_output))

    def track(self):
        while not self.stop_event.is_set():
            for tracker in self.trackers:
                if tracker.initialization_event.is_set():
                    if len(self.mouse_clicks[tracker.camera_id]) < 2:
                        continue

                    clicks = self.mouse_clicks[tracker.camera_id][:2]
                    bbox = tracker.create_bounding_box(*clicks)
                    if len(bbox) != 4:
                        continue
                    tracker.initialize_tracker(bbox)
                    tracker.initialization_event.clear()
                else:
                    if tracker.tracker is None:
                        continue
                    try:
                        tracker.track()
                    except Exception:
                        print("Tracker failed on the image. Skipping it.")
            time.sleep(0)


class Tracker(object):
    def __init__(self, tracker_type, cam_ind, obj_ind, coordinates, image_stream, initialization_event, console_output):
        self.tracker = None
        self.coordinates = coordinates
        self.image_stream = image_stream
        self.tracker_type = tracker_type
        self.initialization_event = initialization_event
        self.last_image_time = -1

        self.object_id = obj_ind
        self.camera_id = cam_ind
        self.uid = get_tracker_uid(cam_ind, obj_ind)
        self.console_output = console_output

    def initialize_tracker(self, bbox, image=None):
        print("Initializing tracker on camera {} at object {}".format(self.camera_id, self.object_id))
        try:
            if image is None:
                image = self.get_newest_image().image

            self.tracker = TrackerFactory.get_tracker(self.tracker_type)
            bbox = tuple(bbox)
            self.tracker.init(image, bbox)
        except Exception:
            self.console_output.append("Initialization failed. Try again.")
            self.tracker = None

    def track(self):
        res = self.get_object_position()
        if res is None:
            return

        point = Point(*res)
        self.coordinates.append(point)

    def get_object_position(self):
        image_entry = self.get_newest_image()
        image, time = image_entry.image, image_entry.timestamp

        if time == self.last_image_time:
            return None

        self.last_image_time = time
        ok, bbox = self.tracker.update(image)

        if not ok:
            return None

        x, y = self.get_bounding_box_center(bbox)
        return ((x, y), time)

    def get_newest_image(self):
        return self.image_stream[-1]

    def get_bounding_box_center(self, bbox):
        return int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2)

    def create_bounding_box(self, corner1, corner2):
        x1, y1 = corner1
        x2, y2 = corner2
        return min(x1, x2), min(y1, y2), abs(x1 - x2), abs(y1 - y2)
