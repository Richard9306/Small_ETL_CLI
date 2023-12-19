import random
from faker import Faker
import json
import csv
from xml.etree import ElementTree as ET


def generate_fake_data():
    fake = Faker()
    data = []
    for _ in range(1000):
        random_amount_children = []
        for _ in range(random.randint(0, 5)):
            random_amount_children.append(
                {"name": fake.first_name(), "age": random.randint(1, 18)})
        record = {
            "firstname": fake.first_name(),
            "telephone_number": random.choice([fake.phone_number(), ""]),
            "email": random.choice([fake.email(), ""]),
            "password": fake.password(),
            "role": random.choice(["admin", "user"]),
            "created_at": fake.date_time().strftime("%Y-%m-%d %H:%M:%S"),
            "children": random_amount_children,
        }
        data.append(record)
    return data


def save_to_json(filename):
    data = generate_fake_data()
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=2)


def save_to_csv(filename):
    data = generate_fake_data()
    with open(filename, "w", newline="") as csv_file:
        fieldnames = data[0].keys()
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=";")
        csv_writer.writeheader()
        for row in data:
            print('Before: ', row)
            new_structure_children = ''
            if row['children']:
                for index in range(len(row['children'])):
                    child = list(row['children'][index].values())
                    name, age = child
                    new_structure_children += name + ',' + str(age) + ';'
                new_structure_children = new_structure_children.rstrip(';')
                print(new_structure_children)
                row['children'] = new_structure_children
            else:
                row['children'] = ''
            print('After: ', row)
            csv_writer.writerow(row)


def save_to_xml(filename):
    data = generate_fake_data()
    root = ET.Element("individuals")
    for entry in data:
        element = ET.SubElement(root, "individual")
        for key, value in entry.items():
            sub_element = ET.SubElement(element, key)
            sub_element.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(filename)



save_to_json("../files_to_load/test_data_json.json")
save_to_csv("../files_to_load/test_data_csv.csv")
save_to_xml("../files_to_load/test_data_xml.xml")