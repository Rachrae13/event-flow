
import pandas as pd
from pathlib import Path

# Find the CSV file in the same folder
file_path = Path(__file__).with_name("events.csv")

# Read the event dataset
events = pd.read_csv(file_path)

# Display all events
print("SMART EVENT AND INTERVAL QUERY MANAGEMENT")
print("------------------------------------------")

print("\nALL COLLEGE EVENTS:\n")
print(events.to_string(index=False))

# Display total number of events
print("\nTotal number of events:", len(events))
