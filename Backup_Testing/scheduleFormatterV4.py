#reportFormatterV4 converts report.txt to a list for use in scheduleTest.py's schedule list.  
# Latest version uses regex instead of fixed values based on indeces for pass, day, sat, aos, los & sat. 
# For example: 
# # #
# Pass,Day of Week,AOS,LOS,Satellite
# 1,0,"(14, 42, 17)","(14, 57, 21)",NOAA-15
# 2,0,"(15, 9, 39)","(15, 24, 4)",NOAA-19
# 3,0,"(15, 18, 23)","(15, 30, 18)",METOP-C
# 4,0,"(16, 5, 7)","(16, 19, 45)",METOP-B
import csv
from datetime import datetime, timezone
import re

def replace_satellite(satellite):
    replacements = {
        "NOAA 15": "NOAA-15",
        "NOAA 18": "NOAA-18",
        "NOAA 19": "NOAA-19"
    }
    return replacements.get(satellite, satellite)

def get_day_time_tuple(date_str):
    date_obj = datetime.strptime(date_str, "%m/%d/%Y %H:%M:%S")
    day_of_week = date_obj.weekday()   # Monday is 0, Sunday is 6
    time_tuple = tuple(map(int, date_obj.strftime("%H %M %S").split()))
    return day_of_week, time_tuple

# Regular expression to match lines with satellite data
pattern = re.compile(r'^(?P<pass>\d{1,4})\s+(?P<satellite>.{19})\s+(?P<aos>\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2}:\d{1,2})\s+(?P<los>\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{1,2}:\d{1,2})')

data = []

with open("/home/noaa_gms/RFSS/Tools/Report_Exports/report.txt", "r") as file:
    for line in file:
        match = pattern.match(line)
        if match:
            pass_number = match.group("pass")
            satellite = replace_satellite(match.group("satellite").strip())
            aos_day, aos_time = get_day_time_tuple(match.group("aos"))
            los_day, los_time = get_day_time_tuple(match.group("los"))
            
            data.append((pass_number, aos_day, aos_time, los_time, satellite))

# Write the data to a CSV file
with open("/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv", "w", newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Pass", "Day of Week", "AOS", "LOS", "Satellite"])
    csv_writer.writerows(data)
