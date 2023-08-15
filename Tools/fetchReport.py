import requests
import datetime
import csv

url = "http://192.168.4.1/report?a=38771;43689;25338;28654;33591"
response = requests.get(url)
data = response.json()["list"][:-1]

today_day_of_week = datetime.datetime.utcnow().weekday()
rows = []

for entry in data:
    satellite = entry[1].replace(" ", "-")
    aos_time = datetime.datetime.utcfromtimestamp(entry[2])
    los_time = datetime.datetime.utcfromtimestamp(entry[3])
    day_of_week = aos_time.weekday()
    max_elevation = entry[7]

    if day_of_week == today_day_of_week and max_elevation > 5.0:
        formatted_aos = f"({aos_time.hour},{aos_time.minute},{aos_time.second})"
        formatted_los = f"({los_time.hour},{los_time.minute},{los_time.second})"
        rows.append((aos_time, day_of_week, formatted_aos, formatted_los, satellite, max_elevation))

rows.sort(key=lambda x: x[0])

output_path = "/home/noaa_gms/RFSS/Tools/Report_Exports/schedule.csv"
with open(output_path, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Pass", "DayofWeek", "AOS", "LOS", "Satellite", "MaxElevation"])
    for index, row in enumerate(rows, start=1):
        writer.writerow([index, row[1], row[2], row[3], row[4], row[5]])

print(f"Schedule exported to {output_path}")
