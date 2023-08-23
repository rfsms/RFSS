from pymongo import MongoClient
import requests
import time
from datetime import datetime

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['status_db']
status_collection = db['status_collection']
pass_log = db['pass_log']

# # Time duration for 48 hours in seconds
# end_time = time.time() + 48 * 60 * 60

while True:
    try:
        status_response = requests.get('http://192.168.4.1/status')
        # pass_response = requests.get('http://192.168.4.1/satlog')

        if status_response.status_code == 200:
            status_data = status_response.json()
            selected_data = {
                "mode": status_data['mode'],
                "time": datetime.utcfromtimestamp(status_data['time']).strftime('%Y-%m-%d %H:%M:%S'),
                "az": status_data['az'],
                "el": status_data['el'],
                "sched": status_data['sched'],
                "voltsAZ": status_data['voltsAZ'],
                "voltsEL": status_data['voltsEL'],
                "msg": status_data['msg'],
                "gpssats": status_data['gpssats'],
                "gpslat": status_data['gpslat'],
                "gpslon": status_data['gpslon'],
                "grid": status_data['grid'],
                "serial": status_data['serial'],
                "gpssats": status_data['gpssats'],
                "gpslat": status_data['gpslat'],
                "gpslon": status_data['gpslon'],
            }
            status_collection.insert_one(selected_data)
            # print(selected_data)

        # if pass_response.status_code == 200:
        #     pass_data = pass_response.json()
        #     for log_item in pass_data['log']:
        #         if len(log_item) == 6:
        #             log_item[4] = datetime.utcfromtimestamp(int(log_item[4])).strftime('%Y-%m-%d %H:%M:%S')
        #             log_item[5] = datetime.utcfromtimestamp(int(log_item[5])).strftime('%Y-%m-%d %H:%M:%S')
        #     pass_log.insert_one(pass_response.json())

    except Exception as e:
        print(f"Error: {e}")
    time.sleep(2)