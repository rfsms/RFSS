import pyvisa
import time
from scipy.io import savemat
import datetime
import os

def opc_check(INSTR):
    """ Check if all preceding commands are completed """
    INSTR.write('*OPC')
    opc_value = INSTR.query('*OPC?').strip()
    # print(f"Initial *OPC? response: {opc_value}")

    # If *OPC? is not 1, enter a loop and wait for it to become 1
    if opc_value != '1':
        while True:
            time.sleep(0.1)  # Small delay to avoid overloading the communication
            opc_value = INSTR.query('*OPC?').strip()
            print(f"Current *OPC? response: {opc_value}")
            if opc_value == '1':
                break

def setup_instrument(ip_address):
    """ Setup VISA instrument """
    rm = pyvisa.ResourceManager('@py')
    INSTR = rm.open_resource(f'TCPIP0::{ip_address}::inst0::INSTR')
    idn = INSTR.query("*IDN?")
    instrument = idn.replace("Hello, I am: ", "")
    print(f"Setting Up '{instrument.split()}'at {INSTR}")
    
    # Setup Spectrum Analyzer
    INSTR.write("*RST")
    INSTR.write("*CLS")
    INSTR.write("SYST:DEF SCR")
    INSTR.write("INST:NSEL 1")
    INSTR.write("INIT:CONT OFF")
    INSTR.write("SENS:FREQ:SPAN 20000000")
    INSTR.write("SENS:FREQ:CENT 1702500000")
    INSTR.write("POW:ATT:AUTO ON")
    # INSTR.write("POW:ATT 0")
    INSTR.write("POW:GAIN ON")
    INSTR.write("BAND 5000")
    INSTR.write("DISP:WIND:TRAC:Y:RLEV -20dBm")
    INSTR.write("TRAC1:TYPE WRIT")
    INSTR.write("DET:TRAC1 NORM")
    INSTR.write("TRAC2:TYPE MAXH")
    INSTR.write("DET:TRAC2 POS")
    INSTR.write("AVER:COUNT 10")
    opc_check(INSTR)
    # print("SA Setup Complete")

    #Create IQ window
    INSTR.write("INST:SCR:CRE")
    INSTR.write("INST:NSEL 8")
    INSTR.write("INIT:CONT ON")
    opc_check(INSTR)
    # print("IQ Window Setup Complete")

    INSTR.write("CONF:WAV")
    INSTR.write("SENS:FREQ:CENT 1702500000")
    INSTR.write("POW:GAIN ON")
    INSTR.write("WAV:SRAT 18.75MHz")
    INSTR.write("WAV:SWE:TIME 160ms")
    INSTR.write("DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON")
    INSTR.write("FORM:BORD SWAP")
    INSTR.write("FORM REAL,32")    
    opc_check(INSTR)
    # print("IQ Setup Complete")
    
    return INSTR


def configure_video_trigger(INSTR):
    """ Configure video trigger on the instrument """
    INSTR.write('TRIG:WAV:SOUR VID')  # Set trigger source to Video
    INSTR.write('TRIG:VID:LEV -55')   # Set the Video trigger level    # Start immediate measurement
    opc_check(INSTR)
    # print("Video Setup Complete")

def determine_quarter_folder_name(current_datetime):
    """ Determine the quarter folder name based on the hour of the day """
    hour = current_datetime.hour
    if hour < 6:
        return '0000-0559'
    elif hour < 12:
        return '0600-1159'
    elif hour < 18:
        return '1200-1759'
    else:
        return '1800-2359'
    
def wait_for_trigger_and_fetch_data(INSTR, DEMOD_DIR, satellite_name, max_wait_time=900):
    """ Wait for the trigger event to occur, fetch and save data """
    print("Polling for trigger...")
    start_time = time.time()

    while True:
        # Check if maximum wait time has been exceeded
        if time.time() - start_time > max_wait_time:
            print("Maximum wait time exceeded. Exiting trigger wait.")
            return False

        operation_status_str = INSTR.query(':STATus:OPERation:CONDition?').strip()
        operation_status_dec = int(operation_status_str)
        
        # Interpret the operation status and print the corresponding state
        if operation_status_dec == 24:
            print(f"Operation Status Register (DEC): {operation_status_dec} -- Triggered, Fetching Data")
            
            # Fetch and process data
            data = INSTR.query_binary_values(":FETCH:WAV0?")

            # Convert to separate I and Q arrays
            i_data = data[::2]
            q_data = data[1::2]

            current_datetime = datetime.datetime.utcnow()

            # Determine folders and file path
            daily_folder_name = current_datetime.strftime('%Y_%m_%d')
            daily_folder = os.path.join(DEMOD_DIR, daily_folder_name)
            os.makedirs(daily_folder, exist_ok=True)

            quarter_folder_name = determine_quarter_folder_name(current_datetime)
            quarter_folder = os.path.join(daily_folder, quarter_folder_name)
            os.makedirs(quarter_folder, exist_ok=True)

            formatted_current_datetime = current_datetime.strftime('%Y%m%d_%H%M%S_UTC')
            mat_file_path = os.path.join(quarter_folder, f'{formatted_current_datetime}_{satellite_name}.mat')

            # Save I/Q data to MAT file
            savemat(mat_file_path, {'I_Data': i_data, 'Q_Data': q_data})
            print(f"Data saved to {mat_file_path}")
            
        # elif operation_status_dec == 8:
        #     print(f"Operation Status Register (DEC): {operation_status_dec} -- Sweeping")
        # elif operation_status_dec == 16:
        #     print(f"Operation Status Register (DEC): {operation_status_dec} -- Measuring")
        # elif operation_status_dec == 56:
        #     print(f"Operation Status Register (DEC): {operation_status_dec} -- Waiting For Trigger")
        # else:
        #     print(f"Operation Status Register (DEC): {operation_status_dec} -- Unknown State")
   
        time.sleep(0.2)

def main():
    ip_address = '192.168.3.101'
    DEMOD_DIR = '/home/noaa_gms/RFSS/Tools/Testing/deleteme'
    satellite_name = 'testing'

    INSTR = setup_instrument(ip_address)
    configure_video_trigger(INSTR)
    wait_for_trigger_and_fetch_data(INSTR, DEMOD_DIR, satellite_name)

    INSTR.close()

if __name__ == "__main__":
    main()
