import threading
from ApplicationProcess import run_application, stop_event, provider

t = threading.Thread(target = run_application, name="Application")
t.setDaemon(True)
t.start()


stop_event.wait()
# while not stop_event.is_set():
#     pass

provider.stop_capturing()
print("Last instruction of mainthread")

for th in threading.enumerate():
    print(th.name, th.isDaemon())

t.join(3.0)