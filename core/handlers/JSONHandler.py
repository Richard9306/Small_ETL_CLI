import json
from HandlerInterface import HandlerInterface

class JSONHandler(HandlerInterface):
    @staticmethod
    def read(file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data
