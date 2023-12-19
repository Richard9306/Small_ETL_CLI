from HandlerInterface import HandlerInterface
from xml.etree import ElementTree as ET


class XMLHandler(HandlerInterface):
    @staticmethod
    def read(file_path):
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

