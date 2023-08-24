from flask import Flask, render_template, request
import pymongo
import datetime
from pytz import timezone

app = Flask(__name__)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["status_db"]
collection = db["schedule_daily"]

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
    if event:
        date_from_db = event['timestamp']
        date_from_db_str = date_from_db.strftime('%Y-%m-%d')
        next_event_found = False
        for item in event['schedule']:
            AOS_time_str = ":".join(map(str, item['AOS']))
            LOS_time_str = ":".join(map(str, item['LOS']))
            AOS_time = datetime.datetime.strptime(AOS_time_str, '%H:%M:%S')
            LOS_time = datetime.datetime.strptime(LOS_time_str, '%H:%M:%S')

            AOS_datetime = date_from_db.replace(hour=AOS_time.hour, minute=AOS_time.minute, second=AOS_time.second)
            LOS_datetime = date_from_db.replace(hour=LOS_time.hour, minute=LOS_time.minute, second=LOS_time.second)

            if AOS_datetime <= current_utc_time <= LOS_datetime:
                item['highlight'] = "blue"
            elif AOS_datetime > current_utc_time and not next_event_found:
                item['highlight'] = "yellow"
                next_event_found = True
            else:
                item['highlight'] = ""

            item['AOS'] = AOS_time_str
            item['LOS'] = LOS_time_str
            item['AOS_EST'] = convert_to_EST(item['AOS'])
            item['LOS_EST'] = convert_to_EST(item['LOS'])

    current_utc_time_str = current_utc_time.strftime("%m/%d/%Y %H:%M")
    return render_template('calendar.html', current_utc_time=current_utc_time_str, event=event['schedule'] if event else None, date_from_db=date_from_db_str)


@app.route('/events', methods=['POST'])
def events():
    selected_date = request.form['date']
    selected_date_obj = datetime.datetime.strptime(selected_date, '%Y-%m-%d')
    next_day_date_obj = selected_date_obj + datetime.timedelta(days=1)
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
    return render_template('events.html', event=event if event else None, selected_date=selected_date, date_from_db=date_from_db_str)

if __name__ == '__main__':
    app.run(debug=True)
