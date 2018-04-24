import Config
class QueuesProvider(object):
    Images = []
    LocalizatedPoints3D = [[] for _ in range(Config.objects_count)]
    TrackedPoints2D = [[] for _ in range(Config.camera_count() * Config.objects_count)]
    MouseClicks = [[] for _ in range(Config.camera_count() * Config.objects_count + 1)]
    ConsoleMessages = []

    @classmethod
    def get_image_with_timestamp(cls, camera_index, image_index = -1):
        return cls.Images[camera_index][image_index]

    @classmethod
    def get_tracked_point_with_timestamp(cls, camera_index, point_index = -1):
        return cls.TrackedPoints2D[camera_index][point_index]

    @classmethod
    def get_located_point(cls, point_index = -1):
        return cls.LocalizatedPoints3D[point_index]

    @classmethod
    def get_mouse_click(cls, window_index, index = -1):
        return cls.MouseClicks[window_index][index]

    @classmethod
    def add_mouse_click(cls, window_index, x, y):
        cls.MouseClicks[window_index].append({'x': x, 'y': y})