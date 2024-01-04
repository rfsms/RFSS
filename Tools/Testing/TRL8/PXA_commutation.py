# import pyvisa
from datetime import datetime
from scipy.io import savemat
import logging

TEMP_DIR = '/home/its/RFSS/Tools/Testing/TRL8/TLR8_Data/'

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
        PXA.write("SENS:FREQ:SPAN 20000000")
        PXA.write("SENS:FREQ:CENT 1702500000")
        # PXA.write("SENS:SWE:POIN 10")
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

        logging.info("Scanning setup complete")

    except Exception as e:
        logging.error(f"Error while setting up instrument for scanning: {e}")

def captureTrace(PXA):
    try:
        # PXA.write("INST:SCR:SEL 'Spectrum Analyzer 1'") #MXB
        PXA.write("INST:SEL SA") #MXA
        PXA.write("INIT:IMM;*WAI")
        trace_data = PXA.query('TRAC? TRACE2')
    
        # PXA.write("INST:SCR:SEL 'IQ Analyzer 1'") #MXB
        PXA.write("INST:SEL BASIC") #MXA

        PXA.write("INIT:IMM;*WAI")
        data = PXA.query_binary_values(":FETCH:WAV0?")

        # Convert to separate I and Q arrays
        i_data = data[::2]
        q_data = data[1::2]

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save I/Q data to MAT file
        savemat(f'{TEMP_DIR}{current_time}.mat', {'I_Data': i_data, 'Q_Data': q_data})

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


