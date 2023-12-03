import sqlite3
import json
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from datetime import datetime



class DatabaseLoader:
    def __init__(self):
        self.conn = None
    def connect_db(self):
        try:
            self.conn = sqlite3.connect('individuals.db')
            print("Utworzono połączenie z bazą danych.")
            return self.conn
        except Exception as e:
            print(f"Błąd podczas tworzenia połączenia z bazą danych: {e}")
            raise
    def insert_data_into_db(self,data):
        cursor = self.conn.cursor()
        try:

            for individual_data in data:
                cursor.execute("""
                INSERT INTO individuals (firstname, telephone_number, email, password, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    individual_data['firstname'],
                    individual_data['telephone_number'],
                    individual_data['email'],
                    individual_data['password'],
                    individual_data['role'],
                    individual_data['created_at']
                ))
                individual_id = cursor.lastrowid
                for child_data in individual_data['children']:
                    cursor.execute("""
                    INSERT INTO children (individual_id, name, age)
                    VALUES (?, ?, ?)
                    """, (
                        individual_id,
                        child_data['name'],
                        child_data['age']
                    ))
            self.conn.commit()
        except Exception as e:
            print(f"Błąd podczas zapisu danych do bazy: {e}")

    def close_connection(self):
        try:
            self.conn.close()
            print("Połączenie z bazą danych zostało zamknięte.")
        except Exception as e:
            print(f"Błąd podczas próby zamknięcia połączenia z bazą danych: {e}")

    def validate_email(self, email):
        if email.count('@') != 1:
            return False
        parts = email.split('@')
        if parts[0].endswith('.') or parts[0].startswith('.') or parts[1].endswith('.')or parts[1].startswith('.'):
            return False
        if len(parts[0]) < 1:
            return False
        if parts[1].count('.'):
            domain_parts = parts[1].split('.')
        else:
            return False
        if len(domain_parts[0]) < 1:
            return False
        if len(domain_parts[-1]) not in range(1, 5):
            return False
        if not domain_parts[-1].isalnum():
            return False
        return email

    def validate_telephone_number(self, telephone_nr):
        cleaned_nr = re.sub(r'\D', '', telephone_nr)
        cleaned_nr = cleaned_nr[-9:]
        return cleaned_nr


class JSONHandler:
    @staticmethod
    def read(file_path):
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
            return data
        except Exception as e:
            print(f"Błąd podczas zczytania pliku {file_path.name}: {e}")
            raise


class CSVHandler:
    @staticmethod
    def read(file_path):
        try:
            data = []
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=';')
                for row in csv_reader:
                    row_data = {}
                    for key, value in row.items():
                        if key == 'children':
                            children_data = []
                            for child_info in value.split(';'):
                                name, age = child_info.split(',')
                                children_data.append({'name': name, 'age': age})
                            row_data[key] = children_data
                        else:
                            row_data[key] = value
                    data.append(row_data)
            return data
        except Exception as e:
            print(f"Błąd podczas zczytania pliku {file_path.name}: {e}")
            raise


class XMLHandler:
    @staticmethod
    def read(file_path):
        try:
            with open(file_path, "r") as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                data = []
                for individual_element in root.findall('individual'):
                    individual_data = {
                        'firstname': individual_element.find('firstname').text,
                        'telephone_number': individual_element.find('telephone_number').text,
                        'email': individual_element.find('email').text,
                        'password': individual_element.find('password').text,
                        'role': individual_element.find('role').text,
                        'created_at': individual_element.find('created_at').text,
                        'children': []
                    }
                    for child_element in individual_element.findall('children/child'):
                        child_data = {
                            'name': child_element.find('name').text,
                            'age': child_element.find('age').text
                        }
                        individual_data['children'].append(child_data)
                    data.append(individual_data)
                return data
        except Exception as e:
            print(f"Błąd podczas zczytania pliku {file_path.name}: {e}")
            raise


if __name__ == "__main__":
    json_path = JSONHandler.read(Path('../files_to_load/data_json.json'))
    csv_path = CSVHandler.read(Path('../files_to_load/data_csv.csv'))
    xml_path = XMLHandler.read(Path('../files_to_load/data_xml.xml'))
    load_data = DatabaseLoader()
    load_data.connect_db()
    load_data.insert_data_into_db(csv_path)
    load_data.insert_data_into_db(json_path)
    load_data.insert_data_into_db(xml_path)
    load_data.close_connection()
    print(load_data.validate_email("john.doe.@.com"))
    print(load_data.validate_email("john.doe@d.com"))
    print(load_data.validate_telephone_number('+48123456789'))
    print(load_data.validate_telephone_number('00123456789'))
    print(load_data.validate_telephone_number('(48) 123456789'))
    print(load_data.validate_telephone_number('123 456 789'))
    print(load_data.validate_telephone_number('123456789'))