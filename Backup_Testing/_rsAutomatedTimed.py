# RFSS VNA Setup and Execution 
# Code setup both Spectrum and IQ instruments, capture screenshot of spectrum analyzer (with spectrogram), move to IQ instrument, run 10 sweeps and then capture IQ data.
# Data is then saved with UTC YMDhms timestamp
# API Reference
# https://rsinstrument.readthedocs.io/en/latest/StepByStepGuide.html
# Preconditions:
# - Installed RsInstrument Python module from pypi.org
# https://www.rohde-schwarz.com/us/faq/how-to-install-update-rsinstrument-package-faq_78704-946496.html
# - Installed VISA e.g. R&S Visa 5.12.x or newer
# https://www.rohde-schwarz.com/us/applications/r-s-visa-application-note_56280-148812.html

from RsInstrument import * 
import time
import datetime

resource_string_1 = 'TCPIP::192.168.1.101::hislip0'  

#Option Strings - will stick with rsVisa
#option_string_empty = ''  # Default setting
#option_string_force_ni_visa = 'SelectVisa=ni'  # Forcing NI VISA usage
option_string_force_rs_visa = 'SelectVisa=rs'  # Forcing R&S VISA usage
#option_string_force_no_visa = 'SelectVisa=SocketIo'  # Socket communication for LAN connections, no need for any VISA installation

# Make sure you have the last version of the RsInstrument
RsInstrument.assert_minimum_version('1.53.0')

# Function to convert UTC string/UTC
def parse_utc_time(utc_time_str):
    return datetime.datetime.strptime(utc_time_str, '%m/%d/%Y %H:%M:%S')

if __name__ == "__main__":

    #Previous semi automated working sample example where start/stop/satName is defined and the code will exceute only for induvidual selections
    # UTC_start_time_str = '7/27/2023 18:54:00'
    # UTC_stop_time_str = '7/27/2023 19:14:00'
    # satName = "METOP1"

    UTC_start_time_str = '7/31/2023 17:42:00'
    UTC_stop_time_str = '7/31/2023 17:42:10'
    satName = "NOAA18"

    UTC_start_time = parse_utc_time(UTC_start_time_str)
    UTC_stop_time = parse_utc_time(UTC_stop_time_str)

    # For use when we will use TLE report.txt file...
    # with open('report.txt', 'r') as file:
    #     lines = file.readlines()
    #     UTC_start_time_str = lines[0].strip()  # assuming the first line is the start time
    #     UTC_stop_time_str = lines[1].strip()  # assuming the second line is the stop time
    #     sat_Name = lines[2].strip() # now pull satName from thrird line

    try:
        print('Preparing Instrument')
        instr = RsInstrument(resource_string_1, False, False, option_string_force_rs_visa) #(Resource, ID Query, Reset, Options)

        # Switch ON logging to the console for troubleshooting SpecAn config issues
        # instr.logger.log_to_console = True
        # instr.logger.mode = LoggingMode.On

        # Instrument Setup
        instr.reset()
        instr.clear_status()

        instr.write("SYST:DISP:UPD ON")
        instr.write("INIT:CONT ON")
        instr.write("SENS:FREQ:CENT 1702500000")
        instr.write("SENS:FREQ:SPAN 20000000")
        instr.write("SENS:BAND:RES 10000")
        instr.write("SENS:BAND:VID:AUTO OFF")
        instr.write("SENS:BAND:VID 50")
        instr.write("INP:ATT:AUTO OFF")
        instr.write("INP:ATT 0")
        instr.write("DISP:WIND1:SUBW:TRAC1:MODE AVER")
        instr.write("SENS:WIND1:DET1:FUNC RMS")
        instr.write("DISP:WIND1:SUBW:TRAC2:MODE MAXH")
        instr.write("SENS:WIND1:DET2:FUNC RMS")
        instr.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL 100")
        instr.write("DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110")
        instr.write("CALC1:SGR:STAT ON")
                
        instr.write("INST:CRE:NEW IQ, 'IQ Analyzer'")
        instr.write("INIT:CONT OFF")
        instr.write("TRAC:IQ:SRAT 18750000")
        instr.write("SENS:SWE:TIME 0.016")
        instr.write("SENS:SWE:COUN 10")

        instr.write("HCOP:DEV:LANG PNG")

        while datetime.datetime.utcnow() < UTC_stop_time:
            if datetime.datetime.utcnow() >= UTC_start_time:

                #Setup timestamps for filenames
                current_datetime = datetime.datetime.utcnow()
                formmatted_current_datetime = current_datetime.strftime('%Y-%m-%d_%H_%M_%S_UTC') 
                print(f"String datetime: {formmatted_current_datetime}")
                time_saved_Spec = f"'C:\\R_S\\Instr\\user\RFSS\{satName}_{formmatted_current_datetime}'"
                time_saved_IQ = f"'C:\\R_S\\Instr\\user\RFSS\{satName}_{formmatted_current_datetime}'"
                
                # Print screenshot of Spectrum Analysis/Spectrogram
                # Have removed the spectrum version to remove duplicates from Matlab code
                #nstr.write(f"MMEM:NAME {time_saved_Spec}")
                #instr.write("HCOP:IMM")
                instr.write("INST IQ")
                # instr.write("INIT:CONT OFF")

                instr.write("INIT:IMM;*WAI")
                print('wating...')
                instr.write(f"MMEM:STOR:IQ:STAT 1,{time_saved_IQ}")

                instr.write("INST:SEL 'Spectrum'")
                instr.write("INIT:CONT ON")

                idn = instr.query_str('*IDN?')

                #Log collection info
                print(f"\nHello, I am: '{idn}'")
                print(f"Current IQ save filename is: {time_saved_IQ}")
                #print(f'RsInstrument driver version: {instr.driver_version}')
                #print(f'Visa manufacturer: {instr.visa_manufacturer}')
                #print(f'Instrument full name: {instr.full_instrument_model_name}')
                #print(f'Instrument installed options: {",".join(instr.instrument_options)}')
            else:
                instr.write("INST:SEL 'Spectrum'")
                instr.write("INIT:CONT ON")
                print('Waiting for start time...')

            time.sleep(5)

    

    except KeyboardInterrupt:
        print("User killed it.")

# Close the session
instr.close()
