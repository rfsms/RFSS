from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

url = "http://192.168.4.1/status"

# Global variables to keep track of schedule and flipped status history
schedule_history = []
flipped_history = []
# azimuth_history = []
# elevation_history = []

@app.route('/')
def index():
    return render_template('status.html')

@app.route('/status_data')
def status_data():
    response = requests.get(url)
    data = {}
    if response.status_code == 200:
        data = json.loads(response.text)
        epoch_time = data['time']
        est_time = datetime.utcfromtimestamp(epoch_time).astimezone(pytz.timezone('US/Eastern'))
        utc_time = datetime.utcfromtimestamp(epoch_time).astimezone(pytz.utc)
        data['time'] = est_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        data['utc_time'] = utc_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')

        # Record azimuth and elevation changes
        # azimuth_history.append((est_time, data['az']))
        # elevation_history.append((est_time, data['el']))

        # Record schedule status changes
        current_schedule_status = "Scheduled" if data['sched'] == 1 else "Unscheduled"
        schedule_history.append((est_time, current_schedule_status))

        # Record flipped status changes
        current_flipped_status = "Flipped" if data['flipped'] == 1 else "Unflipped"
        flipped_history.append((est_time, current_flipped_status))

        # Limit history to last 24 hours
        current_time = datetime.now(pytz.timezone('US/Eastern'))
        schedule_history[:] = [event for event in schedule_history if event[0] > current_time - timedelta(hours=48)]
        flipped_history[:] = [event for event in flipped_history if event[0] > current_time - timedelta(hours=48)]
        # azimuth_history[:] = [event for event in azimuth_history if event[0] > current_time - timedelta(hours=48)]
        # elevation_history[:] = [event for event in elevation_history if event[0] > current_time - timedelta(hours=48)]


    return jsonify(data=data, schedule_history=[(time.strftime('%Y-%m-%d %H:%M:%S %Z%z'), status) for time, status in schedule_history],
        flipped_history=[(time.strftime('%Y-%m-%d %H:%M:%S %Z%z'), status) for time, status in flipped_history])


if __name__ == '__main__':
    app.run(debug=True)
