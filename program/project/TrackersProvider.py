import Config
from TrackerFactory import TrackerFactory


def get_tracker_uid(cam_ind, obj_ind):
    return cam_ind * Config.objects_count + obj_ind

class TrackersProvider(object):
    def __init__(self, images1, images2, mouse_clicks, coordinates, stop_event, initialization_events, tracker_type = 'KCF', number_of_tracked_objects = 1):
        self.image_streams = [images1, images2]
        self.object_count = number_of_tracked_objects
        self.tracker_type = tracker_type
        self.mouse_clicks = mouse_clicks
        self.initialization_events = initialization_events
        self.coordinates = coordinates
        self.stop_event = stop_event

        self.trackers = []
        for cam_ind, image_stream in enumerate(self.image_streams):
            for obj_ind in range(self.object_count):
                uid = get_tracker_uid(cam_ind, obj_ind)
                print("Append tacker with uid=", uid, "cam_ind=", cam_ind, "obj_ind=", obj_ind)
                self.trackers.append(
                    Tracker(cam_ind=cam_ind, obj_ind=obj_ind,
                            tracker_type = tracker_type,
                            image_stream=image_stream,
                            coordinates=self.coordinates[uid],
                            initialization_event=self.initialization_events[uid]))

    def track(self):
        while not self.stop_event.is_set():

            for tracker in self.trackers:
                if tracker.initialization_event.is_set():
                    if len(self.mouse_clicks[tracker.camera_id]) < 2:
                        continue

                    clicks = self.mouse_clicks[tracker.camera_id][-2:]
                    bbox = tracker.create_bounding_box(*clicks)
                    tracker.initialize_tracker(bbox)
                    tracker.initialization_event.clear()
                else:
                    if tracker.tracker is None:
                        continue
                    tracker.track()

class Tracker(object):
    def __init__(self, tracker_type, cam_ind, obj_ind, coordinates, image_stream, initialization_event):
        self.tracker = None
        self.coordinates = coordinates
        self.image_stream = image_stream
        self.tracker_type = tracker_type
        self.initialization_event = initialization_event

        self.object_id = obj_ind
        self.camera_id = cam_ind
        self.uid = get_tracker_uid(cam_ind, obj_ind)

    def initialize_tracker(self, bbox, image = None):
        print("Initializing tracker on camera", self.camera_id, "at object", self.object_id)

        if image is None:
            time, image = self.get_newest_image()
            if image is None:
                return False

        self.tracker = TrackerFactory.get_tracker(self.tracker_type)
        ok = self.tracker.init(image, bbox)

    def track(self):
        time, position = self.get_object_position()
        self.coordinates.append((time, position))
        #if self.camera_id == 1:
        #    print("Added new coordinates", position)

    def get_object_position(self, image = None):
        if image is None:
            time, image = self.get_newest_image()
            #print(self.camera_id, id(image), id(self))

        ok, bbox = self.tracker.update(image)

        if ok:
            x, y = self.get_bounding_box_center(bbox)
            return (time, (x, y))
        else:
            return None, None

    def get_newest_image(self):
        if len(self.image_stream) == 0:
            return None

        time, image = self.image_stream[-1]
        return time, image

    def get_bounding_box_center(self, bbox):
        return int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2)

    def create_bounding_box(self, left_upper_corner, right_bottom_corner):
        x1, y1 = left_upper_corner['x'], left_upper_corner['y']
        x2, y2 = right_bottom_corner['x'], right_bottom_corner['y']
        return (x1, y1, x2 - x1, y2 - y1)

