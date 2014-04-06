import json
import os

from functools import partial
from os.path import isfile, join


__all__ = ["FilesystemDataSets"]


class DataSets(object):
    def get(self, id):
        pass

    def list(self):
        pass


class NotFound(StandardError):
    pass


def load_json_file(filename):
    with open(filename) as f:
        return json.load(f)


def add_self_link(data_set):
    data_set['self'] = "http://localhost:8080/data-sets/{}".format(data_set['id'])
    return data_set

class FilesystemDataSets(object):
    BASE_PATH = "./data/data-sets"

    def get(self, id):
        file_path = "{}/{}.json".format(self.BASE_PATH, id)
        if not os.path.isfile(file_path):
            raise NotFound
        return add_self_link(load_json_file(file_path))

    def list(self):
        abspath = partial(join, self.BASE_PATH)
        return map(add_self_link,
            map(load_json_file,
                filter(isfile, 
                    map(abspath, os.listdir(self.BASE_PATH)))))
