import sqlite3
from pathlib import Path
import re
from json_xml_csv_handlers import JSONHandler, CSVHandler, XMLHandler
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.unique_emails = []
        self.unique_telephone_numbers = []
        self.unique_entries = []

    def connect_db(self):
        try:
            self.conn = sqlite3.connect("individuals.db")
            print("Connection with database is open.")
            return self.conn
        except Exception as e:
            print(f"An error occured while connecting to the database: {e}")
            exit(1)

    def create_database(self):
        cursor = self.conn.cursor()
        creation_script = """
        CREATE TABLE IF NOT EXISTS individuals (
            individual_id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            telephone_number TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT,
            created_at DATETIME 
        );
        CREATE TABLE IF NOT EXISTS children (
            child_id INTEGER PRIMARY KEY AUTOINCREMENT,
            individual_id INTEGER NOT NULL,
            name TEXT,
            age INTEGER,
            FOREIGN KEY (individual_id) REFERENCES individuals(individual_id)
        );
        """
        cursor.executescript(creation_script)
        self.conn.commit()
        print("Creating database: done.")

    def insert_data_into_db(self, data, filepath):
        cursor = self.conn.cursor()
        try:
            valid_data = self.validate_data_and_check_duplicates(data)
            if valid_data:
                for individual_data in valid_data:
                    are_any_duplicates = self.are_any_duplicates_for_login_in_db(
                        individual_data, cursor
                    )
                    if are_any_duplicates:
                        cursor.execute(
                            """
                        INSERT INTO individuals (firstname, telephone_number, email, password, role, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                            (
                                individual_data["firstname"],
                                individual_data["telephone_number"],
                                individual_data["email"],
                                individual_data["password"],
                                individual_data["role"],
                                individual_data["created_at"],
                            ),
                        )
                        individual_id = cursor.lastrowid
                        for child_data in individual_data["children"]:
                            cursor.execute(
                                """
                            INSERT INTO children (individual_id, name, age)
                            VALUES (?, ?, ?)
                            """,
                                (individual_id, child_data["name"], child_data["age"]),
                            )
                        self.conn.commit()
                        print(
                            f"Data from file: {filepath.name} for {individual_data['firstname'], individual_data['email']} inserted into database."
                        )
                print(f"All data has been imported to database from {filepath.name}.")
        except sqlite3.IntegrityError as e:
            print(
                f"An error occurred during inserting data into database from file: {filepath.name}: {e}"
            )
            self.conn.close()
            exit(1)

    def close_connection(self):
        try:
            self.conn.close()
            print("Connection with database is closed.")
        except Exception as e:
            print(f"An error occured while closing the connection with database: {e}")
            exit(1)

    def validate_email(self, email):
        if not email:
            return False
        if email.count("@") != 1:
            return False
        parts = email.split("@")
        if (
            parts[0].endswith(".")
            or parts[0].startswith(".")
            or parts[1].endswith(".")
            or parts[1].startswith(".")
        ):
            return False
        if len(parts[0]) < 1:
            return False
        if parts[1].count("."):
            domain_parts = parts[1].split(".")
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
        cleaned_nr = re.sub(r"\D", "", telephone_nr)
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
            validated_email = self.validate_email(entry["email"])
            validated_telephone_nr = self.validate_telephone_number(
                entry["telephone_number"]
            )
            if validated_email and validated_telephone_nr:
                if (
                    validated_email not in self.unique_emails
                    and validated_telephone_nr not in self.unique_telephone_numbers
                ):
                    self.unique_emails.append(validated_email)
                    self.unique_telephone_numbers.append(validated_telephone_nr)
                    entry["telephone_number"] = validated_telephone_nr
                    self.unique_entries.append(entry)
                    valid_data.append(entry)
                else:
                    for u_entry in self.unique_entries:
                        if (
                            validated_email in u_entry.values()
                            and validated_telephone_nr in u_entry.values()
                        ):
                            is_new_entry_newer = self.compare_datetimes(
                                u_entry["created_at"], entry["created_at"]
                            )
                            if is_new_entry_newer:
                                valid_data.append(entry)
                                self.unique_entries.remove(u_entry)
                                self.unique_entries.append(entry)

        return valid_data

    def are_any_duplicates_for_login_in_db(self, individual_data, cursor):
        query = "SELECT * FROM individuals WHERE email = ? OR telephone_number = ?"
        cursor.execute(
            query, (individual_data["email"], individual_data["telephone_number"])
        )
        result = cursor.fetchall()
        if result:
            result = result[0]
            is_new_entry_newer = self.compare_datetimes(
                result[6], individual_data["created_at"]
            )
            if is_new_entry_newer:
                cursor.execute(
                    """
                UPDATE individuals SET firstname = ?, telephone_number = ?, email = ?, password = ?, role = ?, created_at = ? WHERE individual_id = ?
                """,
                    (
                        individual_data["firstname"],
                        individual_data["telephone_number"],
                        individual_data["email"],
                        individual_data["password"],
                        individual_data["role"],
                        individual_data["created_at"],
                        result[0],
                    ),
                )
                cursor.execute(
                    f"""DELETE FROM children WHERE individual_id = {result[0]}"""
                )
                for child_data in individual_data["children"]:
                    cursor.execute(
                        """
                    INSERT INTO children (individual_id, name, age)
                    VALUES (?, ?, ?)
                    """,
                        (result[0], child_data["name"], child_data["age"]),
                    )
                self.conn.commit()

        return not result

    def compare_datetimes(self, datetime1, datetime2):
        datetime_format = "%Y-%m-%d %H:%M:%S"
        datetime1 = datetime.strptime(datetime1, datetime_format)
        datetime2 = datetime.strptime(datetime2, datetime_format)
        return datetime1 < datetime2

    def clean_db(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM individuals")
        cursor.execute("DELETE FROM children")
        self.conn.commit()

    def load_data(self, json_path, csv_path, xml_path):
        json_data = JSONHandler.read(json_path)
        csv_data = CSVHandler.read(csv_path)
        xml_data = XMLHandler.read(xml_path)
        try:
            self.insert_data_into_db(json_data, json_path)
            self.insert_data_into_db(csv_data, csv_path)
            self.insert_data_into_db(xml_data, xml_path)
        except Exception as e:
            print(f"An error occurred while loading data into database: {e}")


if __name__ == "__main__":
    json_path = Path("../tests/test_data_json.json")
    csv_path = Path("../files_to_load/data_csv.csv")
    xml_path = Path("../files_to_load/data_xml.xml")

    load_data = DatabaseManager()
    load_data.connect_db()
    load_data.load_data(json_path, csv_path, xml_path)
    # load_data.clean_db()
    load_data.close_connection()
