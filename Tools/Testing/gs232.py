import serial
import time

def send_command(serial_port, command):
    print(f"Sending command: {command}")
    serial_port.write(f'{command}\r\n'.encode())
    time.sleep(0.5)
    response = serial_port.read_all().decode().strip()
    print(f"Received response: {response}")
    return response

def get_position(serial_port):
    response = send_command(serial_port, 'C2')
    parts = response.split()
    if len(parts) == 2:
        azimuth = parts[0].split('=')[1]
        elevation = parts[1].split('=')[1]
        return int(azimuth), int(elevation)
    else:
        raise ValueError("Invalid response format: " + response)

def set_azimuth(serial_port, azimuth):
    current_azimuth, current_elevation = get_position(serial_port)
    command = f'W{int(azimuth):03d} {current_elevation:03d}'
    send_command(serial_port, command)

def set_elevation(serial_port, elevation):
    current_azimuth, current_elevation = get_position(serial_port)
    command = f'W{current_azimuth:03d} {int(elevation):03d}'
    send_command(serial_port, command)

def wait_for_position(serial_port, target_azimuth, target_elevation, tolerance=1):
    while True:
        current_azimuth, current_elevation = get_position(serial_port)
        if abs(current_azimuth - target_azimuth) <= tolerance and abs(current_elevation - target_elevation) <= tolerance:
            break
        time.sleep(1)  # Wait for a short period before checking again

# Example usage
if __name__ == "__main__":
    port = '/dev/ttyUSB0'
    baud_rate = 9600
    target_azimuth = 90
    target_elevation = 45

    with serial.Serial(port, baud_rate, timeout=1) as serial_port:
        print("Setting azimuth to 90 degrees...")
        set_azimuth(serial_port, target_azimuth)
        print("Setting elevation to 45 degrees...")
        set_elevation(serial_port, target_elevation)

        print("Waiting for rotor to reach target position...")
        wait_for_position(serial_port, target_azimuth, target_elevation)

        print("Current position:")
        position = get_position(serial_port)
        print(position)
