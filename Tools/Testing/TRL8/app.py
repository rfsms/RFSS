from flask import Flask, render_template, jsonify
import os
from PXA_commutation import instrument_setup, captureTrace
from multiprocessing import Process, Manager
import eventlet
from flask_socketio import SocketIO
import pyvisa
import logging

# Reset the Root Logger - this section is used to reset the root logger and then apply below configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/Tools/Testing/TRL8/scan.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initialize logger
logger = logging.getLogger(__name__)

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

manager = Manager()
shared_data = manager.dict()
shared_data['is_scanning'] = False  # Initialize the flag

# pyvisa.log_to_screen()

# Global process variable
scan_process = None
RM = None
PXA = None
RESOURCE_STRING = 'TCPIP::192.168.3.101::hislip0' 

def continuous_capture(shared_data):
    global PXA
    while True:
        if not shared_data.get('is_scanning'):
            break

        try:
            trace_data = captureTrace(PXA)
            shared_data['trace_data'] = trace_data
        except Exception as e:
            logging.info(f"Error in continuous_capture: {e}")
        
        eventlet.sleep(1)

def emit_trace_data():
    with app.app_context():
        while True:
            if shared_data.get('trace_data'):
                socketio.emit('new_data', {'data': shared_data['trace_data']})
                shared_data['trace_data'] = None  # Clear after emitting
            eventlet.sleep(1)  # Adjust as needed

@app.route('/')
def index():
    return render_template('captures.html', flag_exists=shared_data['is_scanning'])

@app.route('/start_scan', methods=['POST'])
def start_scan():
    global RM, PXA    
    RM = pyvisa.ResourceManager() 
    PXA = RM.open_resource(RESOURCE_STRING, timeout=20000)
    instrument_setup(PXA, RESOURCE_STRING)
    shared_data['is_scanning'] = True
    scan_process = Process(target=continuous_capture, args=(shared_data,))
    scan_process.start()
    eventlet.spawn(emit_trace_data)
    return jsonify({'status': 'Scanning Started'})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    global scan_process, PXA
    shared_data['is_scanning'] = False
    if scan_process:
        scan_process.join()
        scan_process = None 
    if PXA:
        PXA.close()

    return jsonify({'status': 'Scanning Stopped'})

@socketio.on('connect')
def handle_connect():
    logging.info("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    logging.info("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8888)
