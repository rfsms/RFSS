from flask import Flask, render_template, jsonify
import eventlet
from flask_socketio import SocketIO
import pyvisa
import logging
from PXA_commutation import instrument_setup, captureTrace

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

shared_data = {'is_scanning': False, 'trace_data': None}
RESOURCE_STRING = 'TCPIP::192.168.3.101::hislip0' 

# pyvisa.log_to_screen()

# Custom log function for SocketIO
def log_socketio_error(event, error_info):
    logging.error(f"Error in SocketIO {event}: {error_info}")

def continuous_capture():
    RM = pyvisa.ResourceManager() 
    PXA = RM.open_resource(RESOURCE_STRING, timeout=20000)
    instrument_setup(PXA, RESOURCE_STRING)
    
    try:
        while shared_data['is_scanning']:
            try:
                trace_data = captureTrace(PXA)
                shared_data['trace_data'] = trace_data
            except Exception as e:
                logging.info(f"Error in continuous_capture: {e}")

            eventlet.sleep(1)  # Non-blocking sleep
    finally:
        if PXA:
            PXA.close()

def emit_trace_data():
    with app.app_context():
        while True:
            if shared_data['trace_data']:
                socketio.emit('new_data', {'data': shared_data['trace_data']})
                shared_data['trace_data'] = None
            eventlet.sleep(1)

@app.route('/')
def index():
    return render_template('captures.html', flag_exists=shared_data['is_scanning'])

@app.route('/start_scan', methods=['POST'])
def start_scan():
    shared_data['is_scanning'] = True
    eventlet.spawn(continuous_capture)
    eventlet.spawn(emit_trace_data)
    return jsonify({'status': 'Scanning Started'})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    shared_data['is_scanning'] = False
    return jsonify({'status': 'Scanning Stopped'})

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
    socketio.run(app, debug=True, host='0.0.0.0', port=8888)
    pass
