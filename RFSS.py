import schedule
import time
import http.client
import datetime
import csv
import RFSS_Autonomous
import logging
import json

# Reset the Root Logger - this section is used to reset the root logger and then apply below configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Change this to increase/decrease schedule based on minimum elevation
minElevation = 5.0

# Check if the current time is 00:00 UTC or later, and if so, call RFSS_Autonomous.main()
if datetime.datetime.utcnow().time() >= datetime.time(0, 0):
    logging.info('fetchReport Script restarted. Using current schedule.')
    RFSS_Autonomous.main()

def fetchReport():
    try:
        logging.info(f"Fetching report for use.")
        conn = http.client.HTTPConnection("192.168.4.1", 80)
        conn.request("GET", "/report?a=38771;43689;25338;28654;33591")
        response = conn.getresponse()

        if response.status == 200:
            data = json.loads(response.read().decode())["list"][:-1]

            # Get the current day of the week and add 1 for tomorrow
            today = datetime.datetime.utcnow().weekday()

            rows = []

            for entry in data:
                satellite = entry[1].replace(" ", "-")
                aos_time = datetime.datetime.utcfromtimestamp(entry[2])
                los_time = datetime.datetime.utcfromtimestamp(entry[3])
                day_of_week = aos_time.weekday()
                max_elevation = entry[7]

                if day_of_week == today and max_elevation > minElevation:
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

            logging.info('New schedule in use extracted and ready for use.')
            RFSS_Autonomous.main()
        
    except Exception as e:
        logging.error(f'An error occuredL {e}')

schedule.every().day.at("00:00").do(fetchReport)

while True:
    schedule.run_pending()
    time.sleep(1)