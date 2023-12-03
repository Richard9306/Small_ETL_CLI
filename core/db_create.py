import sqlite3

conn = sqlite3.connect('individuals.db')
cursor = conn.cursor()
sql_script = """
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
cursor.executescript(sql_script)
conn.commit()
conn.close()