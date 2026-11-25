
from database import connect_db


def add_event(event_name, department, venue,
              event_date, start_time, end_time):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO events
        (event_name, department, venue,
         event_date, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event_name,
        department,
        venue,
        event_date,
        start_time,
        end_time
    ))

    connection.commit()
    connection.close()


def get_all_events():

    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT event_id, event_name, department,
               venue, event_date, start_time, end_time
        FROM events
        ORDER BY event_date, start_time
    """)

    events = cursor.fetchall()

    connection.close()

    return events


def delete_event(event_id):

    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM events WHERE event_id = ?",
        (event_id,)
    )

    connection.commit()

    deleted_count = cursor.rowcount

    connection.close()

    return deleted_count

def check_venue_conflict(
    venue, event_date, start_time, end_time
):

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT event_id, event_name, start_time, end_time
        FROM events
        WHERE LOWER(TRIM(venue)) = LOWER(TRIM(?))
          AND event_date = ?
          AND start_time < ?
          AND end_time > ?
    """, (
        venue,
        event_date,
        end_time,
        start_time
    ))

    conflicts = cursor.fetchall()

    connection.close()

    return conflicts
