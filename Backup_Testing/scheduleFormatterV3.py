#reportFormatterV3 converts report.txt to a list for use in scheduleTest.py's schedule list.  
# Latest version uses regex instead of fixed values based on indeces for sat, aos, los  
# For example: 
# #
# "Day of Week","AOS","LOS","Satellite"
# 0,"(23, 44, 21)","(23, 52, 55)","NOAA-15"
# 1,"(1, 19, 35)","(1, 34, 27)","NOAA-15"
# 1,"(1, 41, 3)","(1, 49, 13)","METOP-B"

import csv
from datetime import datetime
import re

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
    day_of_week = date_obj.weekday() + 1   # Monday is 0, Sunday is 6
    time_tuple = tuple(map(int, date_obj.strftime("%H %M %S").split()))
    return day_of_week, time_tuple

# Regular expression to match lines with satellite data
pattern = re.compile(r"^\d+\s+(?P<satellite>[\w\s\d\-]+)\s+(?P<aos>[\d\/]+ \d+:\d+:\d+)\s+(?P<los>[\d\/]+ \d+:\d+:\d+)")

data = []

with open("/home/noaa_gms/RFSS/Tools/Report_Exports/report.txt", "r") as file:
    for line in file:
        match = pattern.match(line)
        if match:
            satellite = replace_satellite(match.group("satellite").strip())
            aos_day, aos_time = get_day_time_tuple(match.group("aos"))
            los_day, los_time = get_day_time_tuple(match.group("los"))
            
            data.append((aos_day, aos_time, los_time, satellite))

# Write the data to a CSV file
with open("/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Day of Week", "AOS", "LOS", "Satellite"])
    csv_writer.writerows(data)
