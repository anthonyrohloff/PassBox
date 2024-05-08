import datetime
import sqlite3

def log_action(action, id):
    # Get and format time
    timestamp_raw = datetime.datetime.now()
    timestamp = timestamp_raw.strftime("%m-%d-%Y %H:%M:%S")

    connection = sqlite3.connect("credentials.db")
    cursor = connection.cursor()

    # Add entry to table
    cursor.execute("INSERT INTO log (id, action, time) VALUES (?, ?, ?)", (id, action, timestamp,))

    connection.commit()
    cursor.close()
    connection.close()