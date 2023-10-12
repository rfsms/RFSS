from flask import Flask, render_template, request, Response
import pymongo
import datetime
from pytz import timezone
import http.client
import json

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["status_db"]
collection = db["schedule_daily"]
schedule_run = db['schedule_run']

def get_location():
    try:
        conn = http.client.HTTPConnection("192.168.4.1", 80)
        
        def get_track_data():
            conn.request("GET", "/track")
            response = conn.getresponse()
            return json.loads(response.read()) if response.status == 200 else None

        data = get_track_data()
        
        return data['gpsgr']
            
    except Exception as e:
        return (f'An error occurred checking the location: {e}')

def get_current_AzEl(conn):
    conn.request("GET", "/track")
    response = conn.getresponse()
    data = json.loads(response.read())
    response.close()
    return round(data['az'], 2), round(data['el'], 2)

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

            if schedule_run_entry and 'processed' in schedule_run_entry and schedule_run_entry['processed'] == "true":
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
    return Response(json_data, content_type='application/json')

@app.route('/set_az', methods=['POST'])
def set_az():
    starting_az = request.form['startingAZ']
    ending_az = float(request.form['endingAZ'])
    conn = http.client.HTTPConnection("192.168.4.1", 80)
    conn.request("GET", f"/cmd?a=P|{starting_az}|0|")
    response = conn.getresponse()
    return '', response.status

if __name__ == '__main__':
    app.run(debug=False)
