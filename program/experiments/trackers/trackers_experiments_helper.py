import cv2
import cv2
import numpy as np

from program.TrackerFactory import TrackerFactory


def get_bounding_box_center(bbox):
    return int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2)

def run_trackers_experiment(gui_on, trackers_to_evaluate, empty_background = None, bbox = None, video = None, hsvbbox = None):
    quite = True

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
        print("BBOX:", bbox)
    trackers = []
    for i, tracker in enumerate(trackers_to_evaluate):
        trackers.append(TrackerFactory.get_tracker(tracker))
        if tracker == 'SIMPLEBACKGROUND':
            if empty_background is None:
                print("For SIMPLEBACKGROUND tracker an image of the background is need to be provided.")
                simbbox = bbox
                if isinstance(bbox, list):
                    simbbox = bbox[i]
                trackers[-1].init(frame, simbbox)
            else:
                image = cv2.imread(empty_background)
                trackers[-1].init(image, bbox)
            continue
        elif tracker == 'HSV' and hsvbbox is not None:
            trackers[-1].init(frame, hsvbbox)
            continue
        elif isinstance(bbox, list):
            trackers[-1].init(frame, bbox[i])
        else:
            trackers[-1].init(frame, bbox)

    ticks_count = [0] * len(trackers)
    distance_from_representative = [0] * len(trackers)
    distances_log = [[] for _ in range(len(trackers))]
    object_lost = [[] for _ in range(len(trackers))]
    frames = 0

    representative_have = True
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

            if i == 0 and not ok:
                representative_have = False
            if i == 0 and ok:
                representative_have = True
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

                if not representative_have:
                    continue
                distance = np.linalg.norm(np.array(representative_center) - np.array(center))
                distances_log[i].append(distance)
                distance_from_representative[i] += distance
            else:
                object_lost[i].append(frames)
                if not quite:
                    print(trackers_to_evaluate[i], "lost the object.")

        if gui_on:
            cv2.imshow('image', frame_trackers)
            cv2.waitKey(1)

    cap.release()
    if gui_on:
        cv2.destroyAllWindows()

    freq = cv2.getTickFrequency()
    print("tracker fps mean_distance std")
    for i, ticks in enumerate(ticks_count):
        ticks_per_frame = ticks / frames
        frames_per_second = freq / ticks_per_frame

        print("{} & {:.2f} & {:.2f} & {:.2f} \\\\".format(trackers_to_evaluate[i], frames_per_second,
                                            distance_from_representative[i] / frames,
                                            np.std(distances_log[i])))

        can_recover(distances_log[i], len(distances_log[0]))
        compute_confusion_matrix(object_lost[0], object_lost[i], frames)

def can_recover(log, representative_count):
    # First number is how many of the estimated position were closer than 80 pixel to the true value
    # Second number is how many images were as found
    threshold = 0.8
    succ = sum(l <= 80 for l in log)
    print("  {:.2f}% - {} - {} / {}, representative {}".format(succ / representative_count * 100, succ / representative_count >= threshold,  succ, len(log), representative_count))

def compute_confusion_matrix(representative, results, count):
    x = [True] * count
    y = [True] * count

    if len(results) == 0 or len(representative) == 0:
        if len(results) == 0:
            print("  Tracker never reported object lost")
        return

    for res in representative:
        x[res - 1] = False

    for res in results:
        y[res - 1] = False

    rejects = [0, 0]

    for i, repre in enumerate(x):
        if repre == False:
            rejects[y[i]] += 1

    threshold = 0.9
    lost_object_count = rejects[0] + rejects[1]
    if lost_object_count == 0:
        succ = 1
    else:
        succ = rejects[0] / lost_object_count
    print("  {:.2f}% - able to detect object lost - {}".format(succ * 100, succ > threshold))
