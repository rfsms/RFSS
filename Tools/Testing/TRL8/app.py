from flask import Flask, render_template, jsonify
import os
from PXA_commutation import instrument_setup, captureTrace

app = Flask(__name__)

@app.route('/')
def index():
    flag_exists = os.path.exists('/home/noaa_gms/RFSS/Tools/Testing/TRL8/flag.txt')
    return render_template('captures.html', flag_exists=flag_exists)

@app.route('/start_scan', methods=['POST'])
def start_scan():
    open('/home/noaa_gms/RFSS/Tools/Testing/TRL8/flag.txt', 'w').close()  # Create an empty flag file
    
    # Setup the PXA
    instrument_setup()
    # Start capturing IQ and data
    captureTrace()

    return jsonify({'status': 'Scanning Started'})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    try:
        os.remove('/home/noaa_gms/RFSS/Tools/Testing/TRL8/flag.txt')  # Remove the flag file
    except FileNotFoundError:
        pass
    # Stop scan logic
    return jsonify({'status': 'Scanning Stopped'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888, use_reloader=True)
