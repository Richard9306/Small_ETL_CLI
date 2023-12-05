import sqlite3
from pathlib import Path
import re
from json_xml_csv_handlers import JSONHandler, CSVHandler, XMLHandler



class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.unique_emails = []
        self.unique_telephone_numbers = []
        self.unique_entries = []
    def connect_db(self):
        try:
            self.conn = sqlite3.connect('individuals.db')
            print("Utworzono połączenie z bazą danych.")
            return self.conn
        except Exception as e:
            print(f"Błąd podczas tworzenia połączenia z bazą danych: {e}")
            exit(1)
    def insert_data_into_db(self, data, filepath):
        cursor = self.conn.cursor()
        try:
            valid_data = self.validate_data_and_check_duplicates(data)
            if valid_data:
                for individual_data in valid_data:
                    are_any_duplicates = self.are_any_duplicates_for_login_in_db(individual_data, cursor)
                    if are_any_duplicates:
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
                        print(f"Dane z pliku {filepath.name} dla {individual_data['firstname'], individual_data['email']} wczytane do bazy.")


        except sqlite3.IntegrityError as e:
            print(f"Błąd podczas zapisu danych do bazy z pliku {filepath.name}: {e}")
            self.conn.close()

    def close_connection(self):
        try:
            self.conn.close()
            print("Połączenie z bazą danych zostało zamknięte.")
        except Exception as e:
            print(f"Błąd podczas próby zamknięcia połączenia z bazą danych: {e}")

    def validate_email(self, email):
        if not email:
            return False
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
        if not telephone_nr:
            return False
        cleaned_nr = re.sub(r'\D', '', telephone_nr)
        if len(cleaned_nr) >= 9:
            cleaned_nr = cleaned_nr[-9:]
            return cleaned_nr
        else:
            return False
    def validate_data_and_check_duplicates(self, data):
        if not data:
            return False
        valid_data = []
        for entry in data:
            validated_email = self.validate_email(entry['email'])
            validated_telephone_nr = self.validate_telephone_number(entry['telephone_number'])
            if validated_email and validated_telephone_nr:

                if validated_email not in self.unique_emails and validated_telephone_nr not in self.unique_telephone_numbers:
                    self.unique_emails.append(validated_email)
                    self.unique_telephone_numbers.append(validated_telephone_nr)
                    entry['telephone_number'] = validated_telephone_nr
                    self.unique_entries.append(entry)
                    valid_data.append(entry)
                else:
                    for u_entry in self.unique_entries:
                        if validated_email in u_entry.values() and validated_telephone_nr in u_entry.values():
                            if u_entry['created_at'] < entry['created_at']:
                                valid_data.append(entry)
                                self.unique_entries.remove(u_entry)
                                self.unique_entries.append(entry)



        return valid_data

    def are_any_duplicates_for_login_in_db(self, individual_data, cursor):
        query = "SELECT * FROM individuals WHERE email = ? OR telephone_number = ?"
        cursor.execute(query, (individual_data['email'], individual_data['telephone_number']))
        result = cursor.fetchall()
        if result:
            result = result[0]
            if result[6] < individual_data['created_at']:
                print(individual_data)
                print(result)
                cursor.execute("""
                UPDATE individuals SET firstname = ?, telephone_number = ?, email = ?, password = ?, role = ?, created_at = ? WHERE individual_id = ?
                """, (
                    individual_data['firstname'],
                    individual_data['telephone_number'],
                    individual_data['email'],
                    individual_data['password'],
                    individual_data['role'],
                    individual_data['created_at'],
                    result[0]
                ))
                cursor.execute(f"""DELETE FROM children WHERE individual_id = {result[0]}""")
                for child_data in individual_data['children']:
                    cursor.execute("""
                    INSERT INTO children (individual_id, name, age)
                    VALUES (?, ?, ?)
                    """, (
                        result[0],
                        child_data['name'],
                        child_data['age']
                    ))
                self.conn.commit()

        return not result

    def clean_db(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM individuals')
        cursor.execute('DELETE FROM children')
        self.conn.commit()





if __name__ == "__main__":
    json_path = Path('../tests/test_data_json.json')
    csv_path = Path('../files_to_load/data_csv.csv')
    xml_path = Path('../files_to_load/data_xml.xml')
    json_data = JSONHandler.read(json_path)
    csv_data = CSVHandler.read(csv_path)
    xml_data = XMLHandler.read(xml_path)
    load_data = DatabaseManager()
    load_data.connect_db()
    load_data.insert_data_into_db(json_data, json_path)
    load_data.insert_data_into_db(xml_data, xml_path)
    load_data.insert_data_into_db(csv_data, csv_path)
    # load_data.clean_db()
    load_data.close_connection()