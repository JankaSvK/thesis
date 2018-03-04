import threading
import logging

from GUI import GUI
from Provider import Provider

logging.getLogger().setLevel(logging.INFO)

provider = Provider([0, 1])
provider.initialize_cameras()
provider.start_capturing()

gui = GUI()
guiThread = threading.Thread(target=gui.start, args=(provider.images,), name="GUI")
guiThread.start()

print("Here")

while not provider.calibrate_cameras():
    print("New calibration")
    pass

print("Cameras calibrated")