
from event_manager import add_event, get_all_events

# Add one sample campus event
add_event(
    "AI Symposium",
    "Computer Science",
    "Auditorium",
    "2026-11-25",
    "10:00",
    "12:00"
)

print("Event added successfully!")

# Retrieve all events
events = get_all_events()

print("\nCAMPUS EVENT RECORDS")

for event in events:
    print(event)
