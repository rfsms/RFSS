import csv
from datetime import datetime, timed elta
import time
import os

def is_within_range(start_datetime, stop_datetime):
    current_datetime = datetime.utcnow()
    return start_datetime <= current_datetime <= stop_datetime

def filter_rows_by_time(rows):
    current_time_utc = datetime.utcnow()
    filtered_rows = []

    for row in rows:
        if len(row) < 3:
            continue

        satellite_name, start_datetime_str, stop_datetime_str = row
        start_datetime = datetime.strptime(start_datetime_str, '%m/%d/%Y %H:%M:%S')
        stop_datetime = datetime.strptime(stop_datetime_str, '%m/%d/%Y %H:%M:%S')

        if start_datetime.date() <= current_time_utc.date() <= stop_datetime.date():
            filtered_rows.append((satellite_name, start_datetime, stop_datetime))

    return filtered_rows

report_file_path = '/home/noaa_gms/RFSS/Tools/Report_Exports/report.csv'

last_modified_time = 0

while True:
    current_modified_time = os.path.getmtime(report_file_path)

    if current_modified_time != last_modified_time:
        last_modified_time = current_modified_time

        with open(report_file_path, 'r') as file:
            reader = csv.reader(file)
            header = next(reader, None)  # Skip the header

            rows = list(reader)
            filtered_rows = filter_rows_by_time(rows)

            if not filtered_rows:
                # No more rows left in the file or all rows are in the past, break out of the loop
                break

            for satellite_name, start_datetime, stop_datetime in filtered_rows:
                while is_within_range(start_datetime, stop_datetime):
                    current_time_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Satellite Name: {satellite_name}, Current Time: {current_time_str}")
                    time.sleep(1)  # Wait for 1 second before printing the next time

    # Wait for 1 second before checking for updates in the file
    time.sleep(1)
