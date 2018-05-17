from collections import deque

from . import Config
import platform

def get_number_of_images():
    if '64' in platform.architecture()[0]:
        return Config.images64bit
    else:
        print("WA: working on 32bit architecture, only {} images stored per camera.".format(Config.images32bit))
        return Config.images32bit

class QueuesProvider(object):
    Images = None
    LocalizatedPoints3D = None
    TrackedPoints2D = None
    MouseClicks = None
    ConsoleMessages = None

    @classmethod
    def initialize(cls):
        cls.Images = [deque([], maxlen=get_number_of_images()) for _ in range(Config.camera_count)]
        cls.LocalizatedPoints3D = [[] for _ in range(Config.objects_count)]
        cls.TrackedPoints2D = [[] for _ in range(Config.camera_count * Config.objects_count)]
        cls.MouseClicks = [[] for _ in range(Config.camera_count + 1)]
        cls.ConsoleMessages = []

    @classmethod
    def add_mouse_click(cls, window_index, x, y):
        cls.MouseClicks[window_index].append((x, y))

    Threads = []  # Only for debugging purposes!
