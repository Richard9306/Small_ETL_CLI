
import csv


class CSVHandler:
    @staticmethod
    def read(file_path):
        data = []
        with open(file_path, "r") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=";")
            for row in csv_reader:
                row_data = {}
                for key, value in row.items():
                    if key == "children":
                        if value:
                            children_data = []
                            for child_info in value.split(","):
                                name, age = child_info.split()
                                age = age.lstrip('(').rstrip(')')
                                children_data.append({"name": name, "age": age})
                            row_data[key] = children_data
                        else:
                            row_data[key] = ""
                    else:
                        row_data[key] = value
                data.append(row_data)
        return data