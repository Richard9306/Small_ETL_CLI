import json



class JSONHandler:
    @staticmethod
    def read(file_path):
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        return data
