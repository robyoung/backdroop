import json
import os

from functools import partial
from os.path import isfile, join


class DataSets(object):
    def get(self, id):
        pass

    def list(self):
        pass


def load_json_file(filename):
    with open(filename) as f:
        return json.load(f)

class FilesystemDataSets(object):
    BASE_PATH = "./data/data-sets"

    def get(self, id):
        file_path = "{}/{}.json".format(self.BASE_PATH, id)
        return load_json_file(file_path)

    def list(self):
        abspath = partial(join, self.BASE_PATH)
        return map(load_json_file,
            filter(isfile, 
                map(abspath, os.listdir(self.BASE_PATH))))
