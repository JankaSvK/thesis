import random

class QueueIteratorManager(object):
    def __init__(self, queues, queue_finished):
        self.queue_iters = [QueueIterator(queue, queue_finished) for queue in queues]
        for it in self.queue_iters:
            it.friends = set(self.queue_iters)


class QueueIterator(object):
    def __init__(self, queue, queue_finished):
        self.queue = queue
        self.queue_finished = queue_finished
        self.last_freeze = False
        self.frozen = None
        self.sub_iterator = iter([])
        self.last_timestamp = -1
        self.friends = {self}

    def __next__(self):
        while True:
            try:
                p = next(self.sub_iterator)
                while p.timestamp <= self.last_timestamp:
                    p = next(self.sub_iterator)
                return p
            except StopIteration:
                if self.last_freeze:
                    raise StopIteration
                self.refresh_all()

    def refresh_all(self):
        for friend in self.friends:
            friend.refresh()

    def refresh(self):
        self.frozen = self.threadsafe_list_copy(self.queue)
        self.sub_iterator = iter(self.frozen)
        if self.queue_finished.is_set():
            self.last_freeze = True

    def threadsafe_list_copy(self, iterable):
        while True:
            try:
                res = list(iterable)
            except RuntimeError:
                pass
            else:
                return res
