import sqlite3
import json
from pathlib import Path

conn = sqlite3.connect('individuals.db')
cursor = conn.cursor()
path = Path('../files_to_load/data_json.json')
with open(path, 'r') as json_file:
    data = json.load(json_file)
    for individual_data in data:
        print(individual_data['firstname'])
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
        parent_id = cursor.lastrowid
        for child_data in individual_data['children']:
            cursor.execute("""
            INSERT INTO children (individual_id, name, age)
            VALUES (?, ?, ?)
            """, (
                parent_id,
                child_data['name'],
                child_data['age']
            ))
conn.commit()
conn.close()