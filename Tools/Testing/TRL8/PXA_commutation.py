# import pyvisa
from datetime import datetime
from scipy.io import savemat
import logging
import csv
import os

BASE_DIR = '/home/its/RFSS/Tools/Testing/TRL8/TLR8_Data/'
TEMP_DIR = ''

span = 20000000
cf = 1702500000
points = 1001

def instrument_setup(PXA, RESOURCE_STRING):
    try:
        logging.info("Starting PXA Instrument Scanning Setup")

        # Instrument reset/setup
        idn = PXA.query("*IDN?")
        instrument = idn.replace("Hello, I am: ", "")
        logging.info(f"Setting Up '{instrument}' at {RESOURCE_STRING}")
        
        #Reset SpecAn
        PXA.write("*RST")
        PXA.write("*CLS")
        PXA.write("SYST:DEF SCR")

        # Setup Spectrum Analyzer
        PXA.write("INST:NSEL 1")
        PXA.write("INIT:CONT OFF")
        # PXA.write("SENS:FREQ:SPAN 20000000")
        # PXA.write("SENS:FREQ:CENT 1702500000")
        # PXA.write("SENS:SWE:POIN 10")
        PXA.write(f"SENS:FREQ:SPAN {span}")
        PXA.write(f"SENS:FREQ:CENT {cf}")
        PXA.write(f"SENS:SWE:POIN {points}")
        PXA.write("POW:ATT:AUTO OFF")
        PXA.write("POW:ATT 0")
        PXA.write("BAND 5000")
        PXA.write("DISP:WIND:TRAC:Y:RLEV -40dBm")
        PXA.write("TRAC1:TYPE WRIT")
        PXA.write("DET:TRAC1 NORM")
        PXA.write("TRAC2:TYPE MAXH")
        PXA.write("DET:TRAC2 POS")
        PXA.write("AVER:COUNT 10")
        #Create IQ window
        # # PXA.write("INST:SCR:CRE") # MXB
        # PXA.write("INST:NSEL 8") # MXB
        PXA.write("INST:SEL BASIC") # MXA
        PXA.write("CONF:WAV")
        PXA.write("SENS:FREQ:CENT 1702500000")
        PXA.write("POW:GAIN ON")
        PXA.write("WAV:SRAT 18.75MHz")
        PXA.write("WAV:SWE:TIME 160ms")
        PXA.write("DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON")
        PXA.write("FORM:BORD SWAP")
        PXA.write("FORM REAL,32")

        # Generate a folder name based on the current date
        datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        datetime_folder_path = os.path.join(BASE_DIR, datetime_str)

        # Check if the folder exists, if not, create it
        if not os.path.exists(datetime_str):
            os.makedirs(datetime_folder_path)

        # Update TEMP_DIR to the new daily folder
        global TEMP_DIR
        TEMP_DIR = datetime_folder_path

        logging.info("Scanning setup complete")

    except Exception as e:
        logging.error(f"Error while setting up instrument for scanning: {e}")

def captureTrace(PXA):
    try:
        # PXA.write("INST:SCR:SEL 'Spectrum Analyzer 1'") #MXB
        PXA.write("INST:SEL SA") #MXA
        PXA.write("INIT:IMM;*WAI")
        trace_data = PXA.query('TRAC? TRACE2')
    
        # Remove newline characters and additional quotes from trace_data and split hte data
        trace_data_clean = trace_data.replace('\n', '').replace('"', '')
        trace_data_list = trace_data_clean.split(',')

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = os.path.join(TEMP_DIR, 'trace_data.csv')
        mat_filename = os.path.join(TEMP_DIR, f'{current_time}.mat')

        start_frequency = cf - (span / 2)
        end_frequency = cf + (span /2)
        step = span / (points - 1)
        frequencies = [start_frequency + i * step for i in range(points)]
        header = ['Timestamp'] + [f'{f/1e6:.5f}' for f in frequencies]

        file_exists = os.path.isfile(csv_filename)

        # Append the trace data to the CSV file
        with open(csv_filename, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            if not file_exists:
                csvwriter.writerow(header)
            csvwriter.writerow([current_time] + trace_data_list)

        # PXA.write("INST:SCR:SEL 'IQ Analyzer 1'") #MXB
        PXA.write("INST:SEL BASIC") #MXA

        PXA.write("INIT:IMM;*WAI")
        data = PXA.query_binary_values(":FETCH:WAV0?")

        # Convert to separate I and Q arrays
        i_data = data[::2]
        q_data = data[1::2]

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save I/Q data to MAT file
        savemat(mat_filename, {'I_Data': i_data, 'Q_Data': q_data})

        return trace_data
    
    except Exception as e:
        logging.error(f"An error occurred during captureTrace: {e}")
        return None
    
# def closeConnection():
#     try:
#         if PXA:
#             PXA.close()
#             logging.info('Closed the SA connection')
#     except Exception as e:
#         logging.error(f"An error occurred during closing the connection: {e}")


