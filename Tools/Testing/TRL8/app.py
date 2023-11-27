from flask import Flask, render_template, jsonify
import os
from PXA_commutation import instrument_setup, captureTrace, closeConnection
from multiprocessing import Process, Manager
import eventlet
from flask_socketio import SocketIO

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

manager = Manager()
shared_data = manager.dict()
shared_data['is_scanning'] = False  # Initialize the flag

def continuous_capture(shared_data):
    while shared_data.get('is_scanning'):
        try:
            trace_data = captureTrace()
            shared_data['trace_data'] = trace_data
        except Exception as e:
            print(f"Error in continuous_capture: {e}")
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
    instrument_setup()
    shared_data['is_scanning'] = True
    process = Process(target=continuous_capture, args=(shared_data,))
    process.start()
    eventlet.spawn(emit_trace_data)  # Start the background task
    return jsonify({'status': 'Scanning Started'})

@app.route('/stop_scan', methods=['POST'])
def stop_scan():
    shared_data['is_scanning'] = False
    closeConnection()
    return jsonify({'status': 'Scanning Stopped'})

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8888)
