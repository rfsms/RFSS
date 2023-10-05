import pyvisa
import re
import datetime
import time
import csv

RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0' 
RM = pyvisa.ResourceManager()
INSTR = RM.open_resource(RESOURCE_STRING, timeout = 20000)

INSTR_DIR = 'D:\\Users\\Instrument\\Documents\\BASIC\\data\\WAV\\results\\RFSS\\'
TEMP_DIR = '/home/noaa_gms/RFSS/Received/'

# Instrument reset/setup
idn = INSTR.query('*IDN?')
instrument = idn.replace("Hello, I am: ", "")

def get_SpecAn_content_and_DL_locally(INSTR):
    try:
        INSTR.write(f'MMEM:CDIR "{INSTR_DIR}"')
        response = INSTR.query('MMEM:CAT?')
        # print(response)

        # Corrected the parsing
        content_list = [re.split(',,', item)[0] for item in re.findall(r'"(.*?)"', response)]
        print("Content list:", content_list)
        
        for item in content_list:
            temp_filename = TEMP_DIR + item
            instrument_filename = INSTR_DIR + item
            print(f"Downloading {item}")

            try:
                INSTR.write(f'MMEM:DATA? "{instrument_filename}"')
                data = INSTR.read_raw()
                if data:
                    with open(temp_filename, 'wb') as f:
                        f.write(data)
            except Exception as e:
                print(f"Error while downloading file '{item}': {str(e)}")

            INSTR.write(f'MMEM:DEL "{item}"')

    except pyvisa.errors.VisaIOError as e:
        if "-256," in str(e):
            print("No files on Spectrum Analyzer to process:", e)

def process_schedule():
    satellite_name = 'NOAAtest'

    INSTR.write('INIT:IMM;*WAI')
    current_datetime = datetime.datetime.utcnow()
    formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
    time_saved_IQ = f"'{INSTR_DIR}{formatted_current_datetime}_{satellite_name}'"
    INSTR.write(f'MMEM:STOR:RES "{time_saved_IQ}"')

    get_SpecAn_content_and_DL_locally(INSTR)

def main():
    #Reset SpecAn
    INSTR.write('*RST')
    INSTR.write('*CLS')
    INSTR.write('SYST:DEF SCR')
    print(f"Setting Up '{instrument.rstrip()}' at {RESOURCE_STRING}")

    # Configure Swept SA
    INSTR.write('DISP:ENAB OFF')
    INSTR.write('INIT:CONT ON')
    INSTR.write('DISP:VIEW SPEC')
    INSTR.write('SENS:FREQ:SPAN 20000000')
    INSTR.write('SENS:FREQ:CENT 1702500000')
    INSTR.write('SENS:BAND:RES 10000')
    INSTR.write('SENS:BAND:VID:AUTO OFF')
    INSTR.write('SENS:BAND:VID 10000')
    INSTR.write('POW:ATT:AUTO OFF')
    INSTR.write('POW:ATT 0')    
    INSTR.write('POW:GAIN ON')
    INSTR.write('TRAC1:DISP ON')
    INSTR.write('TRAC1:TYPE WRIT')
    INSTR.write('DET:TRACE1 AVER')
    INSTR.write('AVER:COUN 1')
    INSTR.write('TRAC2:DISP ON')
    INSTR.write('TRAC2:TYPE MAXH')
    INSTR.write('DET:TRACE2 AVER')
    INSTR.write('DISP:WIND:TRAC:Y:RLEV -50')
    INSTR.write('DISP:VIEW:SPEC:HUE 10')
    INSTR.write('DISP:VIEW:SPEC:REF 75')
    INSTR.write('DISP:VIEW:SPEC:BOTT 0')

    # Setup IQ Analyzer
    INSTR.write('INST:SCR:CRE')
    INSTR.write('INST:SEL BASIC')
    INSTR.write('CONF:WAV')
    INSTR.write('SENS:FREQ:CENT 1702500000')
    INSTR.write('POW:ATT:AUTO OFF')
    INSTR.write('POW:ATT 0')    
    INSTR.write('POW:GAIN ON')
    INSTR.write('DISP:WAV:VIEW:NSEL 1')
    INSTR.write('POW:GAIN ON')
    INSTR.write('WAV:SRAT 18.75MHz')
    INSTR.write('WAV:SWE:TIME 16ms')
    INSTR.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')

    # try:
    #     process_schedule()
    #     INSTR.write('DISP:ENAB ON')
    #     RM.close()
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    INSTR.write('INIT:IMM;*WAI')
    INSTR.write(f'MMEM:STOR:RES "D:\\Users\\Instrument\\Documents\\BASIC\\data\\WAV\\results\\testcapture.csv"')

    INSTR.write(':FORM %s,%d' % ('INT', 32))
    INSTR.write(':FORM:BORD %s' % ('SWAP'))
    INSTR.write(':INIT:FCAP')
    INSTR.write('*WAI')
    fcapture = INSTR.query_binary_values(':FETC:FCAP?','f',False)
    print(fcapture)

    # # Create a timestamp
    # current_datetime = datetime.datetime.utcnow()
    # formatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC')

    # # Open a CSV file for writing
    # with open('/home/noaa_gms/RFSS_PXA/fcapture_data.csv', 'a', newline='') as csvfile:
    #     csv_writer = csv.writer(csvfile)
    
    #     # Write timestamp and data to the CSV
    #     csv_writer.writerow([formatted_current_datetime] + fcapture)

    RM.close()

if __name__ == "__main__":
    main()


