#!/usr/bin/python3

## Reading parameters
import cv2
import time
import Config
from OptionParser import parse_options
import threading

options = parse_options()

if options.objects_count is not None:
    Config.objects_count = int(options.objects_count)

## Starting application
stop_event = threading.Event()
from ApplicationProcess import run_application
t = threading.Thread(target = run_application, name="Application", args=(stop_event, options))
t.setDaemon(True)
t.start()

stop_event.wait()

## Exiting application
t.join(1.0)

time.sleep(0.5) # Time for releasing video captures