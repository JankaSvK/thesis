class CustomTracker(object):
    name = 'CUSTOMTRACKER'

    def init(self, image, bbox):
        return True

    # Return status, bbox
    def update(self, image):
        return (True, ((0, 0, 1, 1)))