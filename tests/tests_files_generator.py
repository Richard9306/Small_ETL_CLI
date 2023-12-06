import random

from faker import Faker
import json
import csv
from xml.etree import ElementTree as ET


def generate_fake_data():
    fake = Faker()
    data = []
    for _ in range(1000):
        record = {
            "firstname": fake.first_name(),
            "telephone_number": fake.phone_number(),
            "email": fake.email(),
            "password": fake.password(),
            "role": random.choice(["admin", "user"]),
            "created_at": fake.date_time().strftime("%Y-%m-%d %H:%M:%S"),
            "children": [
                {"name": fake.first_name(), "age": random.randint(1, 18)},
                {"name": fake.first_name(), "age": random.randint(1, 18)},
            ],
        }
        data.append(record)
    return data


def save_to_json(data, filename):
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=2)


def save_to_csv(data, filename):
    with open(filename, "w", newline="") as csv_file:
        fieldnames = data[0].keys()
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        csv_writer.writeheader()
        csv_writer.writerows(data)


def save_to_xml(data, filename):
    root = ET.Element("individuals")
    for entry in data:
        element = ET.SubElement(root, "individual")
        for key, value in entry.items():
            sub_element = ET.SubElement(element, key)
            sub_element.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(filename)


data = generate_fake_data()
save_to_json(data, "test_data_json.json")
save_to_csv(data, "test_data_csv.csv")
save_to_xml(data, "test_data_xml.xml")
