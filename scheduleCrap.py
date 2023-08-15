import http.client
import datetime
import csv
import RFSS_Autonomous
import logging
import json

# Change this to increase/decrease schedule based on minimum elevation
minElevation = 5.0

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/output_file.txt', level=logging.info, format='%(message)s')
print = logging.info

def fetchReport():
    print("Fetching tomorrow's report for use")
    conn = http.client.HTTPConnection("192.168.4.1", 80)
    conn.request("GET", "/report?a=38771;43689;25338;28654;33591")
    response = conn.getresponse()

    # logging.debug(f"Request URL: {url}")
    # logging.debug(f"Request Headers: {response.request.headers}")
    # logging.debug(f"Response Status: {response.status_code}")
    # logging.debug(f"Response Headers: {response.headers}")

    if response.status == 200:
        data = json.loads(response.read().decode())["list"][:-1]



        # Get the current day of the week and add 1 for tomorrow
        tomorrow = (datetime.datetime.utcnow().weekday() + 1) % 7

        rows = []

        for entry in data:
            satellite = entry[1].replace(" ", "-")
            aos_time = datetime.datetime.utcfromtimestamp(entry[2])
            los_time = datetime.datetime.utcfromtimestamp(entry[3])
            day_of_week = aos_time.weekday()
            max_elevation = entry[7]

            if day_of_week == tomorrow and max_elevation > minElevation:
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
        RFSS_Autonomous.main()
        
    
fetchReport()
