
import sqlite3
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).with_name("campus_events.db")


def connect_db():
    return sqlite3.connect(DB_PATH)


def create_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            department TEXT NOT NULL,
            venue TEXT NOT NULL,
            event_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_table()
    print("Campus Event Database created successfully!")
