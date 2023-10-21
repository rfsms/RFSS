# import pyvisa
# import csv
# import datetime
# import struct

# FSV_RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0::INSTR' 
# RM = pyvisa.ResourceManager()

# # Open a connection to the Spectrum Analyzer
# with RM.open_resource(FSV_RESOURCE_STRING) as FSV:
#     pxa_idn = FSV.query('*IDN?')
#     print(f'PXA: {pxa_idn}')

#     FSV.visa_timeout = 20000
#     # FSV.write('SYST:DISP:UPD ON')
#     # FSV.write('INIT:CONT ON')
#     # FSV.write('SENS:FREQ:CENT 1702500000')
#     # FSV.write('SENS:FREQ:SPAN 8000000')
#     # FSV.write('SENS:BAND:RES 5000')
#     # FSV.write('SENS:BAND:VID:AUTO OFF')
#     # FSV.write('SENS:BAND:VID 5000')
#     # FSV.write('INP:ATT:AUTO OFF')
#     # FSV.write('INP:ATT 0')
#     # FSV.write('DISP:WIND:SUBW:TRAC:Y:SCAL:RLEV -30')
#     # FSV.write('DISP:WIND1:SUBW:TRAC1:MODE AVER')
#     # FSV.write('SENS:WIND1:DET1:FUNC RMS')
#     # FSV.write('DISP:WIND1:SUBW:TRAC2:MODE MAXH')
#     # FSV.write('SENS:WIND1:DET2:FUNC RMS')
#     # FSV.write('DISP:WIND1:SUBW:TRAC1:Y:SCAL 100') 
#     # FSV.write('DISP:WIND1:SUBW:TRAC1:Y:SCAL:RPOS 110')
#     # FSV.write('CALC1:SGR:STAT ON')
#     # FSV.write('CALC2:SGR:COL RAD')
#     # FSV.write("INST:CRE:NEW IQ, 'IQ Analyzer'")

#     # FSV.write('INIT:CONT OFF')
#     # FSV.write('TRAC:IQ:SRAT 6250000')
#     # FSV.write('SENS:SWE:TIME 0.016')
#     # FSV.write('SENS:SWE:COUN 10')
#     # FSV.write('HCOP:DEV:LANG PNG')

#     FSV.write('INST IQ')
#     FSV.write('INIT:IMM;*WAI')

#     iq_data_type = FSV.query("TRAC:IQ:DATA:FORM?; WAI")
#     print(f'IQ Type: {iq_data_type}')

#     # FSV.write('FORM REAL,64')
#     #FSV.write('FORM ASC,0') 

#     FSV.write('INST IQ')
#     FSV.write('INIT:IMM;*WAI')

#     iq_data_str = FSV.query("TRAC:IQ:DATA?")
#     iq_data = list(map(float, iq_data_str.replace(',', '').split(';')))
#     i_data = iq_data[::2]
#     q_data = iq_data[1::2]

#     # FSV.write('FORM ASC,0')
#     # form_type = FSV.query("FORM?")
#     # print(f'Format: {form_type}')

#     # # Fetch the IQ data from the spectrum analyzer
#     # iq_data_bin = FSV.query_binary_values('TRAC:IQ:DATA?; WAI', datatype='f', is_big_endian=True)
    
#     # i_data = iq_data_bin[::2]
#     # q_data = iq_data_bin[1::2]

#     # # print("I Data:", i_data)
#     # # print("Q Data:", q_data)
#     # print("Number of elements:", len(iq_data_bin))

#     # If you want to print the I/Q pairs with a newline between each
#     # for i, q in zip(i_data, q_data):
#     #     print(f"I: {i}, Q: {q}\n")

#     csv_file_path = f'test.csv'


#     with open(csv_file_path, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['I_Data', 'Q_Data'])
#         writer.writerows(zip(i_data, q_data))

# WORKING....
import pyvisa
from scipy.io import savemat, loadmat

FSV_RESOURCE_STRING = 'TCPIP::192.168.1.101::hislip0::INSTR'
RM = pyvisa.ResourceManager()

with RM.open_resource(FSV_RESOURCE_STRING) as FSV:
    FSV.visa_timeout = 20000

    FSV.write('INST IQ')
    FSV.write('INIT:IMM;*WAI')

    iq_data_type = FSV.query("FORM?")
    print(f'IQ Type: {iq_data_type}')

    tr_data_type = FSV.query("TRAC:IQ:DATA:FORM?")
    print(f'IQ Type: {tr_data_type}')

    FSV.write("TRAC:IQ:DATA:FORM IQP")

    FSV.write("TRAC:IQ:DATA?")
    iq_data = FSV.read_raw()

    # Convert the bytes to a string and split it
    iq_data_str = iq_data.decode('utf-8')
    iq_data_list = iq_data_str.split(',')

    # Convert strings to floats
    iq_data_floats = list(map(float, iq_data_list))

    # Separate I and Q data
    i_data = iq_data_floats[::2]
    q_data = iq_data_floats[1::2]

    # Save to a .mat file
    savemat('iq_data.mat', {'I_Data': i_data, 'Q_Data': q_data})

    # To confirm the file format is correct
    # Load the .mat file
    mat_data = loadmat('iq_data.mat')

    # Extract and print the I and Q data arrays
    loaded_i_data = mat_data['I_Data'][0]
    loaded_q_data = mat_data['Q_Data'][0]

    print("Loaded I Data:", loaded_i_data)
    print("Loaded Q Data:", loaded_q_data)
