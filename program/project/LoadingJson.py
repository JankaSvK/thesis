import json

class Foo(object):
    def __init__(self, jsonFile = None):
        if jsonFile is None:
            self.x = 1
            self.y = 2
        else:
            with open(jsonFile, 'r') as input:
                self.__dict__ = json.load(input)

    def write_data(self, fileName):
        with open(fileName, 'w') as output:
            json.dump(self.__dict__, output)

print(a)