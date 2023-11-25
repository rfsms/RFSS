from flask import Flask, render_template, jsonify
import os
from PXA_commutation import instrument_setup, captureTrace, closeConnection
from multiprocessing import Process
import eventlet
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Global process variable
scan_process = None

def continuous_capture():
    while os.path.exists('/home/noaa_gms/RFSS/Tools/Testing/TRL8/flag.txt'):
        trace_data = captureTrace()
        socketio.emit('new_data', {'data': trace_data})
        eventlet.sleep(1)
        
@app.route('/')
def index():
    flag_exists = os.path.exists('/home/noaa_gms/RFSS/Tools/Testing/TRL8/flag.txt')
    return render_template('captures.html', flag_exists=flag_exists)

@app.route('/start_scan', methods=['POST'])
def start_scan():
    global scan_process
    open('/home/noaa_gms/RFSS/Tools/Testing/TRL8/flag.txt', 'w').close()
    
    if scan_process is None or not scan_process.is_alive():
        # Setup the PXA
        instrument_setup()
        # Start capturing IQ and data in a separate process
        scan_process = Process(target=continuous_capture)
        scan_process.start()

    return jsonify({'status': 'Scanning Started'})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    global scan_process
    try:
        os.remove('/home/noaa_gms/RFSS/Tools/Testing/TRL8/flag.txt')
    except FileNotFoundError:
        pass

    if scan_process and scan_process.is_alive():
        scan_process.terminate()
        scan_process.join()
        scan_process = None
    
    closeConnection()
    return jsonify({'status': 'Scanning Stopped'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8888)
