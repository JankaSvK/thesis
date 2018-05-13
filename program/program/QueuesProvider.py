from collections import deque

from . import Config


class QueuesProvider(object):
    Images = None
    LocalizatedPoints3D = None
    TrackedPoints2D = None
    MouseClicks = None
    ConsoleMessages = None

    @classmethod
    def initialize(cls):
        cls.Images = [deque([], maxlen=500) for _ in range(Config.camera_count)]
        cls.LocalizatedPoints3D = [[] for _ in range(Config.objects_count)]
        cls.TrackedPoints2D = [[] for _ in range(Config.camera_count * Config.objects_count)]
        cls.MouseClicks = [[] for _ in range(Config.camera_count + 1)]
        cls.ConsoleMessages = []

    @classmethod
    def add_mouse_click(cls, window_index, x, y):
        cls.MouseClicks[window_index].append((x, y))

    Threads = []  # Only for debugging purposes!
