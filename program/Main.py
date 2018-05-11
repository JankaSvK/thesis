#!/usr/bin/python3

import time
import threading
from program.OptionParser import parse_options
from program.ApplicationProcess import run_application

options = parse_options()

## Starting application
stop_event = threading.Event()

t = threading.Thread(target=run_application, name="Application", args=(stop_event, options))
t.setDaemon(True)
t.start()

stop_event.wait()

## Exiting application
t.join(1.0)

time.sleep(0.5)  # Time for releasing video captures
