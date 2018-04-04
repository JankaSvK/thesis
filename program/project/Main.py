import threading
from ApplicationProcess import run_application, stop_event, provider

## Reading parameters


## Starting application
t = threading.Thread(target = run_application, name="Application")
t.setDaemon(True)
t.start()

stop_event.wait()

## Exiting application
t.join(3.0)