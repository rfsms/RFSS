#reportFormatterV2 convert report.txt to a list for use in scheduleTest.py's schedule list
# For example: 
# #
# "Day of Week","AOS","LOS","Satellite"
# 0,"(23, 44, 21)","(23, 52, 55)","NOAA-15"
# 1,"(1, 19, 35)","(1, 34, 27)","NOAA-15"
# 1,"(1, 41, 3)","(1, 49, 13)","METOP-B"

import csv
from datetime import datetime

def replace_satellite(satellite):
    replacements = {
        "NOAA 15": "NOAA-15",
        "NOAA 18": "NOAA-18",
        "NOAA 19": "NOAA-19"
    }
    return replacements.get(satellite, satellite)

def get_day_time_tuple(date_str):
    date_format = "%m/%d/%Y %H:%M:%S"
    date_obj = datetime.strptime(date_str, date_format)
    day_of_week = date_obj.weekday()  # Monday is 0, Sunday is 6
    time_tuple = tuple(map(int, date_obj.strftime("%H %M %S").split()))
    return day_of_week, time_tuple

# Read the file and extract specific columns from each row of the table
with open("/home/noaa_gms/RFSS/Tools/Report_Exports/report.txt", "r") as file:
    lines = file.readlines()

table_started = False
columns_to_print = [1, 2, 3]  # Column indices: 1 for Satellite, 2 for AOS, and 3 for LOS

# Calculate the number of rows to print excluding the header and last 5 rows
rows_to_print = len(lines) - 5

# Create a list to store the extracted data
data = []

for i, line in enumerate(lines):
    if line.strip().startswith("----"):
        table_started = True
        continue  # Skip the line with "----" as it's just a table separator

    if table_started and i < rows_to_print:
        satellite = line[5:20].strip()
        aos = line[20:43].strip()
        los = line[43:66].strip()

        # Replace the satellite name if it matches the specified patterns
        satellite = replace_satellite(satellite)

        # Get day of the week (numeric) and time tuple for AOS and LOS
        aos_day, aos_time = get_day_time_tuple(aos)
        los_day, los_time = get_day_time_tuple(los)

        data.append((aos_day, aos_time, los_time, satellite))

# Write the data to a CSV file
with open("/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    csv_writer.writerow(["Day of Week", "AOS", "LOS", "Satellite"])
    csv_writer.writerows(data)