import datetime
import csv

num_of_entries = 5  # Adjust this to the desired number of rows in your CSV

now = datetime.datetime.utcnow()
start_times = [(now + datetime.timedelta(seconds=10 + i*20)).time() for i in range(num_of_entries)]
end_times = [(now + datetime.timedelta(seconds=20 + i*20)).time() for i in range(num_of_entries)]

with open("/home/noaa_gms/RFSS/Backup_Testing/schedule.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Day of Week", "AOS", "LOS", "Satellite"])
    for i in range(num_of_entries):
        writer.writerow([now.weekday() + 1, str((start_times[i].hour, start_times[i].minute, start_times[i].second)), 
                         str((end_times[i].hour, end_times[i].minute, end_times[i].second)), f"NOAA-{15 + i}"])
