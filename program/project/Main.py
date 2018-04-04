## Reading parameters
from OptionParser import parse_options
options = parse_options()

## Starting application
import threading
from ApplicationProcess import run_application, stop_event, provider

t = threading.Thread(target = run_application, name="Application", args=(options,))
t.setDaemon(True)
t.start()

stop_event.wait()

## Exiting application
t.join(3.0)