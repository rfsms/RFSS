from flask import Flask, render_template, request, Response
import pymongo
import datetime
from pytz import timezone
from http.client import http, RemoteDisconnected
import json
import os
from multiprocessing import Process
import time
import subprocess

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["status_db"]
collection = db["schedule_daily"]
schedule_run = db['schedule_run']

is_paused = False

def get_location():
    try:
        conn = http.client.HTTPConnection("192.168.4.1", 80)
        
        def get_track_data():
            conn.request("GET", "/track")
            response = conn.getresponse()
            conn.close()
            return json.loads(response.read()) if response.status == 200 else None

        data = get_track_data()
        return data['gpsgr']
            
    except Exception as e:
        return (f'An error occurred checking the location: {e}')

def get_current_AzEl(conn):
    conn.request("GET", "/min")
    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    return round(data['az'], 1), round(data['el'], 1)

def format_time(time_tuple):
    return f"{time_tuple[0]:02d}:{time_tuple[1]:02d}:{time_tuple[2]:02d}"

def convert_to_EST(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    utc_time = datetime.time(hours, minutes, seconds)
    utc_dt = datetime.datetime.combine(datetime.date.today(), utc_time, tzinfo=timezone('UTC'))
    est_dt = utc_dt.astimezone(timezone('US/Eastern'))
    return est_dt.strftime('%H:%M:%S')

@app.route('/')
def calendar():
    current_utc_time = datetime.datetime.utcnow()
    today_date_obj = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    next_day_date_obj = today_date_obj + datetime.timedelta(days=1)
    event = collection.find_one({"timestamp": {"$gte": today_date_obj, "$lt": next_day_date_obj}})
    date_from_db_str = None  # Initialize to a default value
    location_data = get_location()
    if event:
        date_from_db = event['timestamp']
        date_from_db_str = date_from_db.strftime('%Y-%m-%d')
        next_event_found = False
        for item in event['schedule']:
            AOS_time_str = ":".join(map(lambda x: str(x).zfill(2), item['AOS']))
            LOS_time_str = ":".join(map(lambda x: str(x).zfill(2), item['LOS']))
            AOS_time = datetime.datetime.strptime(AOS_time_str, '%H:%M:%S')
            LOS_time = datetime.datetime.strptime(LOS_time_str, '%H:%M:%S')

            AOS_datetime = date_from_db.replace(hour=AOS_time.hour, minute=AOS_time.minute, second=AOS_time.second)
            LOS_datetime = date_from_db.replace(hour=LOS_time.hour, minute=LOS_time.minute, second=LOS_time.second)

            # Creating a row representation to match the schedule_daily collection
            row_representation = [
                str(item['Pass']),
                str(item['DayofWeek']),
                f"({','.join(map(str, item['AOS']))})",
                f"({','.join(map(str, item['LOS']))})",
                str(item['Satellite']),
                str(item['MaxElevation'])
            ]

            if AOS_datetime <= current_utc_time <= LOS_datetime:
                item['highlight'] = "blue"
            # Check if the current time is after the current LOS and before the next AOS
            elif AOS_datetime > current_utc_time and not next_event_found:
                item['highlight'] = "yellow"
                next_event_found = True
            else:
                item['highlight'] = ""

            # Query the schedule_run collection based on the row
            schedule_run_entry = schedule_run.find_one({"row": row_representation})

            if schedule_run_entry and 'processed' in schedule_run_entry and str(schedule_run_entry['processed']).lower() == "true":
                item['highlight'] = "grey"

            item['AOS'] = AOS_time_str
            item['LOS'] = LOS_time_str
            item['AOS_EST'] = convert_to_EST(item['AOS'])
            item['LOS_EST'] = convert_to_EST(item['LOS'])

    current_utc_time_str = current_utc_time.strftime("%m/%d/%Y %H:%M")
    return render_template('calendar.html', current_utc_time=current_utc_time_str, event=event['schedule'] if event else None, date_from_db=date_from_db_str, location=location_data)


@app.route('/events', methods=['POST'])
def events():
    selected_date = request.form['date']
    selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d')
    next_day_date_obj = selected_date_obj + datetime.timedelta(days=1)
    date_from_db_str = None  # Initialize to a default value
    location_data = get_location()
    event = collection.find_one({
        "timestamp": {
            "$gte": selected_date_obj,
            "$lt": next_day_date_obj
        }
    })
    if event:
        date_from_db = event['timestamp']
        date_from_db_str = date_from_db.strftime('%Y-%m-%d') 
        for item in event['schedule']:
            item['AOS'] = format_time(item['AOS'])
            item['LOS'] = format_time(item['LOS'])
            item['AOS_EST'] = convert_to_EST(item['AOS'])
            item['LOS_EST'] = convert_to_EST(item['LOS'])
    current_utc_time = datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M")
    return render_template('events.html', event=event if event else None, selected_date=selected_date, date_from_db=date_from_db_str, location=location_data)

@app.route('/get_actual_AzEl')
def get_actual_AzEl():
    conn = http.client.HTTPConnection("192.168.4.1", 80)
    current_az, current_el = get_current_AzEl(conn)
    json_data = json.dumps({'actual_az': current_az, 'actual_el': current_el})
    conn.close()
    return Response(json_data, content_type='application/json')

@app.route('/pause_schedule', methods=['POST'])
def pause_schedule():
    with open("/home/noaa_gms/RFSS/pause_flag.txt", "w") as f:
        f.write("paused")
    global is_paused
    is_paused = True
    conn = http.client.HTTPConnection("192.168.4.1", 80)

    # Send a stop command to the rotor (which also commands SAT Tracker to unschedule)
    conn.request("GET", f"/cmd?a=S")
    response = conn.getresponse()
    conn.close()
    return '', response.status

@app.route('/unpause_schedule', methods=['POST'])
def unpause_schedule():
    if os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
        os.remove("/home/noaa_gms/RFSS/pause_flag.txt")
    global is_paused
    is_paused = False
    conn = http.client.HTTPConnection("192.168.4.1", 80)

    # Re-enable scheduler
    conn.request("GET", "/cmd?a=B|E")
    conn.getresponse()

    # Get schedule to determine if there is an ongoing pass
    conn.request("GET", "/future?a=28654;33591;38771;43689;") #NOAA18 28654;NOAA19 33591;METOPB 38771;METOPC 43689
    response_content = conn.getresponse().read()
    data = json.loads(response_content.decode('utf-8'))

    # Getting the current time in epoch and 
    # Determine which satellite is currently between AOS and LOS
    current_time = int(datetime.datetime.utcnow().timestamp())
    current_utc_time_str = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    sorted_list = sorted(data['list'], key=lambda x: x[2] if len(x) > 9 else float('inf'))

    result = {
        'status': 'success',
        'message': ''
    }

    if sorted_list:
        entry = sorted_list[0]
        if len(entry) > 9:
            aos, los, sat_id = entry[2], entry[3], entry[9]
            print(f"Satellite ID: {sat_id}, AOS: {datetime.datetime.utcfromtimestamp(aos).strftime('%Y-%m-%d %H:%M:%S')} UTC, LOS: {datetime.datetime.utcfromtimestamp(los).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
            # If there is an ongoing pass, then send the command to track it
            # Otherwise SATTracker is an idiot and will wait until the next pass
            if aos <= current_time <= los:
                print(f"Updating satellite with ID {sat_id}")
                conn.request("GET", f"/cmd?a=U|{sat_id}")
                conn.getresponse()
                result['message'] = f'Updating satellite with ID {sat_id} at {current_utc_time_str} UTC'
            else:
                result['message'] = 'No ongoing pass found'

        else:
            result['status'] = 'failure'
            result['message'] = 'No data found'

    conn.close()
    return json.dumps(result), 200, {'Content-Type': 'application/json'}

def set_rotor_azimuth(starting_az, ending_az):
    conn = http.client.HTTPConnection("192.168.4.1", 80)
    try:
        max_retries = 3
        retry_delay = 2  # seconds
        
        def send_request(az):
            retries = 0
            while retries < max_retries:
                try:
                    conn.request("GET", f"/cmd?a=P|{az}|{0}|")
                    response = conn.getresponse()
                    return response
                except RemoteDisconnected:
                    print("Remote end closed connection. Retrying...")
                    retries += 1
                    time.sleep(retry_delay)
            raise Exception("Max retries reached")
        
        # Set initial azimuth
        response = send_request(starting_az)
        print(f"Setting rotor to starting azimuth: {starting_az}, HTTP Status: {response.status}")

        # Wait until the rotor reaches the starting azimuth
        while True:
            current_az, _ = get_current_AzEl(conn)
            if abs(current_az - float(starting_az)) <= 1.0:
                print(f"Rotor is now at starting azimuth: {current_az}")
                break
            time.sleep(1)

            # Check if the operation should be stopped before scanning starts
            if not os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                print("Rotor scanning setup stopped.")
                return

        # Step through azimuth angles
        set_az = float(starting_az)
        while set_az <= float(ending_az):
            #Check is the operation should be stopped while scanning is on-going
            if not os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
                print("Rotor scanning operation stopped.")
                return  # Stop the function if pause_flag.txt does not exist

            conn.request("GET", f"/cmd?a=P|{set_az}|{0}|")
            response = conn.getresponse()
            print(f"Setting rotor to azimuth: {set_az}, HTTP Status: {response.status}")

            try:
                subprocess.run(["python3", "/home/noaa_gms/RFSS/Tools/Testing/PXA_Spectrogram_IQ.py", int(some_data)]], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Trace capture failed with error: {e}")
                continue  # Skip to the next iteration or handle the error as needed

            set_az += 2.0

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

@app.route('/set_az', methods=['POST'])
def set_az_route():
    starting_az = float(request.form['startingAZ'])
    ending_az = float(request.form['endingAZ'])

    # Start scanning task in a separate process
    p = Process(target=set_rotor_azimuth, args=(starting_az, ending_az))
    p.start()
    
    return json.dumps({"message": "Data capture started"}), 200

# Working config before changes for scanning
# @app.route('/set_az', methods=['POST'])
# def set_az():
#     starting_az = request.form['startingAZ']
#     ending_az = float(request.form['endingAZ'])
#     set_az = starting_az
#     conn = http.client.HTTPConnection("192.168.4.1", 80)
#     conn.request("GET", f"/cmd?a=P|{set_az}|{0}|")
#     response = conn.getresponse()
#     return '', response.status

@app.route('/check_pause_state', methods=['GET'])
def check_pause_state():
    paused = os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt")
    return Response(json.dumps({"paused": paused}), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=False)
