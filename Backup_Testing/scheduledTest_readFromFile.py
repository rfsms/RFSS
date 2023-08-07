import csv
import datetime
import time
import pytz
import sys

def custom_print(*args, **kwargs):
    # Custom print function to handle both console and file output
    output_file.write(' '.join(map(str, args)))
    output_file.write("\n")  # Add a newline after each print

# Path to the CSV file
csv_file_path = "/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv"

# Convert the schedule times to UTC timezone and sort by start time
utc = pytz.UTC
utc_schedule = []

with open(csv_file_path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the first line (header)
    for row in reader:
        day = int(row[0])
        start_time_str = row[1].strip('()').split(', ')
        start_time = datetime.time(int(start_time_str[0]), int(start_time_str[1]), int(start_time_str[2]))
        end_time_str = row[2].strip('()').split(', ')
        end_time = datetime.time(int(end_time_str[0]), int(end_time_str[1]), int(end_time_str[2]))
        label = row[3]
        utc_schedule.append((day, start_time, end_time, label))

utc_schedule.sort(key=lambda entry: entry[1])  # Sort by start_time (entry[1])

while True:
    now = datetime.datetime.now(tz=utc)
    current_day = now.weekday()

    for day, start_time, end_time, label in utc_schedule:
        if current_day == day:
            if start_time <= now.time() <= end_time:
                # Redirect output to a file inside the loop
                with open('output_file.txt', 'a') as output_file:
                    sys.stdout = output_file
                    # Execute your function here with the corresponding label
                    custom_print(f"Function with label '{label}' is running!")
                break  # Stop checking other entries for this minute

    # Redirect output to a file inside the loop
    with open('output_file.txt', 'a') as output_file:
        sys.stdout = output_file
        # Print current time in UTC
        custom_print("Current time (UTC):", now)

    # Wait for 1 minute before checking again
    time.sleep(60)
