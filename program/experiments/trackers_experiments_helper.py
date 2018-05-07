from context import program

import cv2
import numpy as np
from program.TrackerFactory import TrackerFactory

def get_bounding_box_center(bbox):
    return int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2)

def run_trackers_experiment(gui_on, trackers_to_evaluate, empty_background = None, bbox = None, video = None):
    if bbox is None:
        select_roi = True
    else:
        select_roi = False

    if video is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video)
        cap.read() # first frame from the video is usually not captured correctly

    ok, frame = cap.read()
    if select_roi:
        bbox = cv2.selectROI(frame, False)
        print(bbox)
    trackers = []
    for i, tracker in enumerate(trackers_to_evaluate):
        trackers.append(TrackerFactory.get_tracker(tracker))
        if tracker == 'SIMPLEBACKGROUND':
            if empty_background is None:
                raise RuntimeError("For SIMPLEBACKGROUND tracker an image of the background is need to be provided.")
            image = cv2.imread(empty_background)
            trackers[-1].init(image, bbox)
            continue
        if isinstance(bbox, list):
            trackers[-1].init(frame, bbox[i])
        else:
            trackers[-1].init(frame, bbox)

    ticks_count = [0] * len(trackers)
    distance_from_representative = [0] * len(trackers)
    object_lost = [[] for _ in range(len(trackers))]
    frames = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if gui_on:
            frame_trackers = np.copy(frame)

        frames += 1

        for i, tracker in enumerate(trackers):
            start = cv2.getTickCount()
            ok, bbox = tracker.update(frame)
            end = cv2.getTickCount()
            ticks_count[i] += end - start

            if ok:
                x, y, w, h = [int(i) for i in bbox]
                if i:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 255)
                    representative_center = get_bounding_box_center(bbox)

                if gui_on:
                    cv2.putText(frame_trackers, trackers_to_evaluate[i], (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, thickness=1)
                    cv2.rectangle(frame_trackers, (x, y), (x + w, y + h), color=color, thickness=2)
                center = get_bounding_box_center(bbox)

                distance = np.linalg.norm(np.array(representative_center) - np.array(center))
                distance_from_representative[i] += distance
            else:
                object_lost[i].append(frames)
                print(trackers_to_evaluate[i], "lost the object.")

        if gui_on:
            cv2.imshow('image', frame_trackers)
            cv2.waitKey(1)

    cap.release()
    if gui_on:
        cv2.destroyAllWindows()

    freq = cv2.getTickFrequency()
    for i, ticks in enumerate(ticks_count):
        ticks_per_frame = ticks / frames
        frames_per_second = freq / ticks_per_frame

        print("{} {:.2f} {:.2f} {} {}".format(trackers_to_evaluate[i], frames_per_second,
                                            distance_from_representative[i] / frames,
                                            len(object_lost[i]), min(object_lost[i], default='None')))

