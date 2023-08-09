import csv
import time
import datetime

file_path = "/home/noaa_gms/RFSS/Backup_Testing/schedule.csv"

# # now availble globally for all functions
# now = datetime.datetime.utcnow()

def print_message(satellite_name):
    """Simple function to print a message."""
    now = datetime.datetime.utcnow()
    print(f'Message processed for {satellite_name} at LOS of {now.strftime("%Y-%m-%d %H:%M:%S")}!')

def process_schedule():
    """Process the schedule CSV."""
    with open(file_path, 'r') as csvfile:
        # Create a CSV reader object
        csvreader = csv.reader(csvfile)
        
        # Skip header
        next(csvreader)

        # Go through rows
        for row in csvreader:
            aos_time = row[1][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            los_time = row[2][1:-1].replace(" ", "").split(",")  # Parsing (hh, mm, ss)
            
            now = datetime.datetime.utcnow()
            satellite_name = row[3]

            # Create los_datetime for today
            los_datetime = datetime.datetime(now.year, now.month, now.day, 
                                             int(los_time[0]), int(los_time[1]), int(los_time[2]))

            # If current time has already passed the scheduled los_datetime, skip to the next schedule
            if now > los_datetime:
                continue
                
            while True:
                now = datetime.datetime.utcnow()  # Update current time at the start of each iteration
                if now >= los_datetime:
                    break
                # intrumentation happens here
                # print(f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(5)  # Sleep for 1 second
            
            print_message(satellite_name)


def main():
    try:
        # Create schedule for debug - Will need to comment out once moved to production
        # This sets up schedule for testing where only thing to input is num_of_entries in the schedule.csv
        # For entries, you can modify start_times/end_times to reflect a larger or smaller window between "passes"
        num_of_entries = 4

        # Delay the first entry by 20 seconds (now + 20), 
        # a pass duration of 10 seconds (event)
        # And a wait duration between (gap) of 20 seconds
        now = datetime.datetime.utcnow() + datetime.timedelta(seconds=20)  
        event_duration = datetime.timedelta(seconds=10)
        gap_duration = datetime.timedelta(seconds=20)
        total_duration = event_duration + gap_duration

        start_times = [(now + i*total_duration) for i in range(num_of_entries)]
        end_times = [(now + i*total_duration + event_duration) for i in range(num_of_entries)]

        with open("/home/noaa_gms/RFSS/Backup_Testing/schedule.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Day of Week", "AOS", "LOS", "Satellite"])
            for i in range(num_of_entries):
                writer.writerow([now.weekday() + 1, 
                                str((start_times[i].hour, start_times[i].minute, start_times[i].second)), 
                                str((end_times[i].hour, end_times[i].minute, end_times[i].second)), 
                                f"NOAA-{15 + i}"])

        

        process_schedule()
        print("Script finished.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
