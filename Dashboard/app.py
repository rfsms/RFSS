from flask import Flask, render_template, request, Response, send_from_directory, abort
import eventlet
from flask_socketio import SocketIO
from werkzeug.utils import safe_join
import logging
import subprocess
import pymongo
import datetime
from pytz import timezone
from http.client import http, RemoteDisconnected
import json
import os
import time
import csv

# Logging setup
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

RESOURCE_STRING = 'TCPIP::192.168.3.101::hislip0' 
OPTION_STRING_FORCE_RS_VISA = 'SelectVisa=rs'
PXA = None
FSV = None
SA_type = None

# Check RFSS service status and log it
result = subprocess.run(["systemctl", "show", "-p", "ExecStart", "RFSS.service"], capture_output=True, text=True)
exec_start_line = result.stdout.strip()
if "RFSS_PXA" in exec_start_line:
    import pyvisa
    from PXA_commutation import instrument_commutation_setup, instrument_scanning_setup, captureTrace, createSpectrogram
    SA_type = "PXA"
    RM = pyvisa.ResourceManager()
    PXA = RM.open_resource(RESOURCE_STRING, timeout=20000)
    logging.info("Imported PXA libraries")
elif "RFSS_FSV" in exec_start_line:
    import RsInstrument
    from FSV_commutation import instrument_commutation_setup, instrument_scanning_setup, captureTrace, createSpectrogram, get_SpecAn_content_and_DL_locally
    SA_type = "FSV"
    FSV = RsInstrument(RESOURCE_STRING, False, False, OPTION_STRING_FORCE_RS_VISA)
    logging.info("Imported FSV libraries")

app = Flask(__name__)
eventlet.monkey_patch()
socketio = SocketIO(app)

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["status_db"]
collection = db["schedule_daily"]
schedule_run = db['schedule_run']

# shared_data = {'is_scanning': False, 'trace_data': None}
is_paused = False
commutateDir = '/home/noaa_gms/RFSS/commutationData'

# Custom log function for SocketIO
def log_socketio_error(event, error_info):
    logging.error(f"Error in SocketIO {event}: {error_info}")

def emit_trace_data(trace_data):
    try:
        formatted_data = [float(i) for i in trace_data.split(',')]
        # logging.info(f"Emitting trace data: {formatted_data}")
        socketio.emit('new_data', {'data': formatted_data})
    except Exception as e:
        logging.error(f"Error emitting trace data: {e}")

def get_location():
    try:
        conn = http.client.HTTPConnection("192.168.4.1", 80)

        def get_track_data():
            conn.request("GET", "/track")
            response = conn.getresponse()
            data = response.read()
            conn.close()
            return json.loads(data) if response.status == 200 else None

        data = get_track_data()
        if 'gpsgr' in data and data['gpsgr']:
            return data['gpsgr']
        
        coords = (round(float(data['lat']), 2), round(float(data['lon']), 2))    
        if coords == (25.77, -80.38):
            return "EL95TS"
        elif coords == (25.73, -80.13):
            return "EL95wr"
        elif coords == (21.35, -157.96):
            return "BL11ai"
        else:
            return f"Coordinates: {coords}"

    except Exception as e:
        return f'An error occurred checking the location: {e}'

def format_time(time_tuple):
    return f"{time_tuple[0]:02d}:{time_tuple[1]:02d}:{time_tuple[2]:02d}"

def convert_to_EST(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    utc_time = datetime.time(hours, minutes, seconds)
    utc_dt = datetime.datetime.combine(datetime.date.today(), utc_time, tzinfo=timezone('UTC'))
    est_dt = utc_dt.astimezone(timezone('US/Eastern'))
    return est_dt.strftime('%H:%M:%S')

def get_current_AzEl(conn):
    conn.request("GET", "/min")
    response = conn.getresponse()
    data = json.loads(response.read())
    return round(data['az'], 1), round(data['el'], 1)

def set_rotor_azimuth(instr, iq_option, starting_az, ending_az, center_frequency_MHz, span_MHz, points, location, band_config):

    logging.info(f"Configuring SA for commutation mode and sending: CF: {center_frequency_MHz}, Span: {span_MHz}, Points: {points}, IQ Conf?: {iq_option}, Band/SR Config: {band_config}")
    instrument_commutation_setup(instr, center_frequency_MHz, span_MHz, points)

    # Calculate the frequency values in MHz with four decimal places
    frequency_start_MHz = center_frequency_MHz - span_MHz / 2
    frequency_end_MHz = center_frequency_MHz + span_MHz / 2
    frequency_step_MHz = span_MHz / (points - 1)
    frequency_values_MHz = [round(frequency_start_MHz + i * frequency_step_MHz, 4) for i in range(points)]

    # Prepare the directory and filename for the CSV
    folderDate = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    dirDate = os.path.join(commutateDir, folderDate)
    if not os.path.exists(dirDate):
        os.makedirs(dirDate)
    
    csv_file_path = os.path.join(dirDate, f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    
    # Initialize the list that will hold all iterations of data
    data_iterations = []
    timestamp_iterations = []

    # print("Starting set_rotor_azimuth function")
    conn = http.client.HTTPConnection("192.168.4.1", 80)
    
    def send_request(az):
        # logging.info(f"Sending request for azimuth: {az}")
        for _ in range(3):
            try:
                conn.request("GET", f"/cmd?a=P|{az}|0|")
                return conn.getresponse()
            except RemoteDisconnected:
                time.sleep(2)
        raise Exception("Max retries reached")

    def check_conditions():
        current_az, current_el = get_current_AzEl(conn)
        logging.info(f"Checking conditions: Current Az: {current_az}, Current El: {current_el}")
        return abs(current_az - float(starting_az)) <= 1.0 and abs(current_el) <= 1.0

    # logging.info("Initial request and conditions check...")
    send_request(starting_az)

    while not check_conditions():
        logging.info("Initial conditions not met. Retrying in 1 second.")
        time.sleep(1)
    
    for set_az in range(int(starting_az), int(ending_az) + 1, 2):
        if os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt"):
            send_request(set_az)
            trace_data = captureTrace(instr, iq=iq_option, set_az=set_az, band=band_config)
            emit_trace_data(trace_data)
            
            data_iterations.append([float(x) for x in trace_data.split(',')])
            timestamp_iterations.append(datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + f'_{set_az}')

        else:
            logging.info("Pause flag removal detected, exiting.")
            return
        
    # Writing to the CSV
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write frequency data as the header row
        header_row = ["Frequency (MHz)"] + timestamp_iterations
        csv_writer.writerow(header_row)

        # Write frequency and amplitude data in corresponding columns for each iteration
        for frequency_MHz, amplitudes in zip(frequency_values_MHz, zip(*data_iterations)):
            row_to_write = [f"{frequency_MHz:.4f}"] + list(amplitudes)
            csv_writer.writerow(row_to_write)

    # Create a spectrogram in the same directory as the CSV file
    createSpectrogram(dirDate, csv_file_path, frequency_start_MHz, frequency_end_MHz, starting_az, ending_az, location)
    logging.info('Commutation scan complete')
    if iq_option and SA_type == "FSV":
        get_SpecAn_content_and_DL_locally(dirDate)
        logging.info(f'Transferred Commutation Data from SA to {dirDate} folder')
        
    unpause_schedule()
    conn.close()

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
    try:
        conn = http.client.HTTPConnection("192.168.4.1", 80)
        current_az, current_el = get_current_AzEl(conn)
        json_data = json.dumps({'actual_az': current_az, 'actual_el': current_el})
        conn.close()
        return Response(json_data, content_type='application/json')
    except Exception as e:
        json_data = json.dumps({'error': str(e)})
        return Response(json_data, content_type='application/json', status=500)

@app.route('/set_az', methods=['POST'])
def set_az_path():
    global PXA, FSV, SA_type
    instr = PXA if SA_type == "PXA" else FSV

    starting_az = float(request.form['startingAZ'])
    ending_az = float(request.form['endingAZ'])
    center_frequency_MHz = float(request.form['centerFreq'])
    span_MHz = float(request.form['span'])
    points = int(request.form['points'])
    location = get_location()
    iq_option = request.form.get('iqOption') == 'on'
    band_config = request.form['bandConfig']
    
    try:
        eventlet.spawn_n(set_rotor_azimuth, instr, iq_option, starting_az, ending_az, center_frequency_MHz, span_MHz, points, location, band_config)
        return json.dumps({"message": "Data capture started"}), 200
    except Exception as e:
        return json.dumps({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/pause_schedule', methods=['POST'])
def pause_schedule():
    logging.info('Schedule paused for commutative mode')
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

    global PXA, FSV, SA_type
    instr = PXA if SA_type == "PXA" else FSV

    # Check if instr is not None
    if instr is None:
        logging.error("Instrument not initialized")
        return json.dumps({"error": "Instrument not initialized"}), 500

    logging.info('Returned SA back to scanning mode')
    instrument_scanning_setup(instr)

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
            # print(f"Satellite ID: {sat_id}, AOS: {datetime.datetime.utcfromtimestamp(aos).strftime('%Y-%m-%d %H:%M:%S')} UTC, LOS: {datetime.datetime.utcfromtimestamp(los).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
            # If there is an ongoing pass, then send the command to track it
            # Otherwise SATTracker is an idiot and will wait until the next pass
            if aos <= current_time <= los:
                logging.info(f"Updating satellite with ID {sat_id}")
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

@app.route('/check_pause_state', methods=['GET'])
def check_pause_state():
    paused = os.path.exists("/home/noaa_gms/RFSS/pause_flag.txt")
    return Response(json.dumps({"paused": paused}), mimetype='application/json')

@app.route('/commutationData')
@app.route('/files/<path:path>')
def list_files(path=''):
    full_path = safe_join(commutateDir, path)
    if os.path.isdir(full_path):
        # List directory contents and sort them by descending (reverse=True) order
        files_and_dirs = sorted(
            os.listdir(full_path),
            key=lambda x: os.path.getmtime(safe_join(full_path, x)),
            reverse=False
        )
        # Then generate HTML for each of the clickable files
        file_links = [
            f'<li><a href="{os.path.join("/files", path, file)}">{file}</a></li>'
            for file in files_and_dirs
        ]
        return f'<ul>{" ".join(file_links)}</ul>'
    elif os.path.isfile(full_path):
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path), as_attachment=False)
    else:
        abort(404)

@socketio.on('connect')
def handle_connect():
    try:
        # Your connect handling logic
        logging.info("Client connected")
    except Exception as e:
        log_socketio_error('connect', str(e))

@socketio.on('disconnect')
def handle_disconnect():
    try:
        # Your disconnect handling logic
        logging.info("Client disconnected")
    except Exception as e:
        log_socketio_error('disconnect', str(e))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port=8080, debug=False) 