import schedule
import time
from datetime import datetime

# Your start and stop date and time (in the format 'M/D/YYYY H:M:S')
start_date_time = '8/3/2023 20:00:00'
stop_date_time = '8/3/2023 21:00:00'

def task_to_execute():
    print("Task executed at:", datetime.now().strftime('%m/%d/%Y %H:%M:%S'))

def check_date_time_range():
    current_datetime = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
    if start_date_time <= current_datetime <= stop_date_time:
        task_to_execute()

# Schedule the check_date_time_range function to run every minute
schedule.every(1).minutes.do(check_date_time_range)

while True:
    schedule.run_pending()
    time.sleep(1)
