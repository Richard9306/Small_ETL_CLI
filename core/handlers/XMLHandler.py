from xml.etree import ElementTree as ET


class XMLHandler:
    @staticmethod
    def read(file_path):
        with open(file_path, "r") as xml_file:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            data = []
            for user_element in root.findall("user"):
                user_data = {
                    "firstname": user_element.find("firstname").text,
                    "telephone_number": user_element.find(
                        "telephone_number"
                    ).text,
                    "email": user_element.find("email").text,
                    "password": user_element.find("password").text,
                    "role": user_element.find("role").text,
                    "created_at": user_element.find("created_at").text,
                    "children": [],
                }
                for child_element in user_element.findall("children/child"):
                    child_data = {
                        "name": child_element.find("name").text,
                        "age": child_element.find("age").text,
                    }
                    user_data["children"].append(child_data)
                data.append(user_data)
            return data

