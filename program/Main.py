#!/usr/bin/python3

## Reading parameters
import cv2
import time
import threading
from program import Config
from program.OptionParser import parse_options

options = parse_options()

if options.objects_count is not None:
    Config.objects_count = int(options.objects_count)

if options.chessboard is not None:
    try:
        chessboard = [int(x) for x in options.chessboard.split(',')]
        Config.chessboard_inner_corners = (chessboard[0], chessboard[1])
        Config.chessboard_square_size = chessboard[2]
    except Exception:
        pass

if options.bbox is not None:
    try:
        if options.bbox.startswith("[[[") and set(options.bbox) <= set("[],0123456789"):
            Config.initial_bounding_boxes = eval(options.bbox)
    except:
        pass

## Starting application
stop_event = threading.Event()

from program.ApplicationProcess import run_application
t = threading.Thread(target = run_application, name="Application", args=(stop_event, options))
t.setDaemon(True)
t.start()

stop_event.wait()

## Exiting application
t.join(1.0)

time.sleep(0.5) # Time for releasing video captures
