import json
import csv
from xml.etree import ElementTree as ET


class JSONHandler:
    @staticmethod
    def read(file_path):
        try:
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
            return data
        except Exception as e:
            print(
                f"An error occurred during the operation on the {file_path.name}: {e}"
            )
            raise


class CSVHandler:
    @staticmethod
    def read(file_path):
        try:
            data = []
            with open(file_path, "r") as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=";")
                for row in csv_reader:
                    row_data = {}
                    for key, value in row.items():
                        if key == "children":
                            children_data = []
                            for child_info in value.split(";"):
                                name, age = child_info.split(",")
                                children_data.append({"name": name, "age": age})
                            row_data[key] = children_data
                        else:
                            row_data[key] = value
                    data.append(row_data)
            return data
        except Exception as e:
            print(
                f"An error occurred during the operation on the {file_path.name}: {e}"
            )
            raise


class XMLHandler:
    @staticmethod
    def read(file_path):
        try:
            with open(file_path, "r") as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                data = []
                for individual_element in root.findall("individual"):
                    individual_data = {
                        "firstname": individual_element.find("firstname").text,
                        "telephone_number": individual_element.find(
                            "telephone_number"
                        ).text,
                        "email": individual_element.find("email").text,
                        "password": individual_element.find("password").text,
                        "role": individual_element.find("role").text,
                        "created_at": individual_element.find("created_at").text,
                        "children": [],
                    }
                    for child_element in individual_element.findall("children/child"):
                        child_data = {
                            "name": child_element.find("name").text,
                            "age": child_element.find("age").text,
                        }
                        individual_data["children"].append(child_data)
                    data.append(individual_data)
                return data
        except Exception as e:
            print(
                f"An error occurred during the operation on the {file_path.name}: {e}"
            )
            raise
