import collections

class Image(dict):

    _index_mapping = [
        'time',
        'image',
        'chessboard',
    ]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self[key] = value
        super(Image, self).__init__(**kwargs)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            key = self._index_mapping[key]
        super(Image, self).__setitem__(key, value)

    def __getitem__(self, item):
        if isinstance(item, int):
            item = self._index_mapping[item]
        return super(Image, self).__getitem__(item)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]
    
    def __iter__(self):
        return iter(self[key] for key in self._index_mapping)