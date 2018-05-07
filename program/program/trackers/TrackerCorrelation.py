import dlib

class CorrelationTracker(object):
	def init(self, image, bbox):
		self.tracker = dlib.correlation_tracker()
		x, y, x2, y2 = bbox
		x2 += x
		y2 +=y
		self.tracker.start_track(image, dlib.rectangle(x, y, x2, y2))
		return True

	def update(self, image):
		self.tracker.update(image)
		out = self.tracker.get_position()
		return (True, (out.left(), out.top(), out.right() - out.left(), out.bottom() - out.top()))
