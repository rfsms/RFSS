import json
import pyvisa
import time
# import subprocess
import os
from scipy.io import savemat, loadmat
from scipy.signal import decimate
from scipy.io.wavfile import write
import numpy as np

# Read vals from the config.json file
config_file_path = '/home/noaa_gms/RFSS/Tools/config.json'
with open(config_file_path, 'r') as json_file:
    config_data = json.load(json_file)

# Read vars from /home/noaa_gms/RFSS/Tools/config.json
analyzerIP = config_data['analyzerIP']
satController = config_data['satController']
span = config_data['span_MHz'] * 1e6
cf = config_data['cf_MHz'] * 1e6 
srat = config_data['srat']
measTime = config_data['measTime']

RM = pyvisa.ResourceManager()
INSTR = RM.open_resource(analyzerIP, timeout = 20000)

def opc_check(INSTR):
    """ Check if all preceding commands are completed """
    INSTR.write('*OPC')
    opc_value = INSTR.query('*OPC?').strip()
    # logging.info(f"OPC Check: {opc_value}")

    # If *OPC? is not 1, enter a loop and wait for it to become 1
    if opc_value != '1':
        while True:
            time.sleep(0.5)
            opc_value = INSTR.query('*OPC?').strip()
            print(f"Current *OPC? response: {opc_value}")
            if opc_value == '1':
                break

# def restart_service():
#     try:
#         print("Attempting to restart RFSS.service")
#         subprocess.run(['sudo', '/home/noaa_gms/RFSS/Tools/restart_RFSS.sh'], check=True)
#         print(f"Successfully requested restart RFSS.service.")
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to restart the RFSS.service: {e}")
#     except Exception as e:
#         print(f"Unexpected error while restarting the RFSS.service: {e}")

def process_schedule():
    # Intrumentation happens here
    INSTR.write('INIT:IMM;*WAI')
    data = INSTR.query_binary_values(":FETCH:WAV0?")
    opc_check(INSTR)

    # Convert to separate I and Q arrays
    i_data = data[::2]
    q_data = data[1::2]

    metadata = {
        'Center_Frequency': cf,
        'Bandwidth': span,
        'Sample_Rate': srat,
        'Measurement_Time': measTime
    }

    mat_file_path = os.path.join('/home/noaa_gms/RFSS/Tools/Testing', 'test.mat')
    savemat(mat_file_path, {'I_Data': i_data, 'Q_Data': q_data, 'Metadata': metadata})

    # mat_data = loadmat(mat_file_path)
    # metadata_array = mat_data['Metadata']
    # print(metadata_array)

    # # Extracting individual elements from the structure
    # center_frequency = metadata_array[0][0][0][0].item()
    # bandwidth = metadata_array[0][0][1][0].item()
    # sample_rate = metadata_array[0][0][2][0]
    # measurement_time = metadata_array[0][0][3][0]

    # # Printing the extracted values
    # print(f"Center Frequency (MHz): {center_frequency/1000000}")
    # print(f"Bandwidth (MHz): {bandwidth/10000}")
    # print(f"Sample Rate (MHz): {sample_rate[0]/100000}")
    # print(f"Measurement Time (ms): {measurement_time[0]*1000}")


def main():
    print("Starting RFSS_PXA main routine")

    # Instrument reset/setup
    idn = INSTR.query("ID?")
    # instrument = idn.replace("Hello, I am: ", "")
    print(f"Setting Up {idn.split()} at {analyzerIP}")
    
    #Reset SpecAn
    INSTR.write("*RST")
    INSTR.write("*CLS")
    INSTR.write("SYST:DEF SCR")
    opc_check(INSTR)
    print("Reset Succesful")

    # Setup Spectrum Analyzer
    INSTR.write("INST:NSEL 1")
    INSTR.write("INIT:CONT OFF")
    INSTR.write(f"SENS:FREQ:SPAN {span}")
    INSTR.write(f"SENS:FREQ:CENT {cf}")
    INSTR.write("POW:ATT:AUTO ON")
    # INSTR.write("POW:ATT 0")
    INSTR.write("POW:GAIN ON")
    INSTR.write(f"BAND 5000")
    INSTR.write("DISP:WIND:TRAC:Y:RLEV -20dBm")
    INSTR.write("TRAC1:TYPE WRIT")
    INSTR.write("DET:TRAC1 NORM")
    INSTR.write("TRAC2:TYPE MAXH")
    INSTR.write("DET:TRAC2 POS")
    INSTR.write("AVER:COUNT 10")
    opc_check(INSTR)
    print("SA Setup Succesful")

    #Create IQ window
    INSTR.write("INST:SCR:CRE")
    INSTR.write("INST:NSEL 8")
    INSTR.write("INIT:CONT OFF")
    INSTR.write("CONF:WAV")
    INSTR.write(f"SENS:FREQ:CENT {cf}")
    # INSTR.write("DISP:WAV:VIEW:NSEL 1")
    INSTR.write("POW:GAIN ON")
    INSTR.write(f"WAV:SRAT {srat}")
    INSTR.write(f"WAV:SWE:TIME {measTime}")
    INSTR.write("DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON")
    INSTR.write("FORM:BORD SWAP")
    INSTR.write("FORM REAL,32")
    opc_check(INSTR)
    print("IQ Setup Succesful")

    try:
        process_schedule()
        INSTR.write("DISP:ENAB ON")
        print("Schedule finished for the day.\n")
    except Exception as e:
        print(f"An error occurred in RFSS_PXA.py main(): {e}")
        # restart_service()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred in RFSS_PXA.py: {e}")