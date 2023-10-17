import pyvisa
import time
import csv
import datetime
import matplotlib.pyplot as plt
import numpy as np

PXA_RESOURCE_STRING = 'TCPIP::192.168.2.101::hislip0::INSTR' 
MXG_RESOURCE_STRING = 'TCPIP::192.168.130.66::5025::SOCKET' 
RM = pyvisa.ResourceManager()
# INSTR_DIR = 'D:\\Users\\Instrument\\Documents\\BASIC\\data\\WAV\\results\\RFSS\\'
# TRACE_DIR = 'D:\\Users\\Instrument\\Documents\\SA\\data\\traces\\RFSS\\'

# Specify the number of times you want to capture the trace
num_capture_iterations = 100

# Initialize a list to store data from each iteration and timestamps
data_iterations = []
timestamp_iterations = []

# pyvisa.log_to_screen()

waveforms_15MHz = [
"2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK.ARB",
"2-1-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_1PRB_GUARDBAND.ARB",
"2-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_2PRB_GUARDBAND.ARB",
"2-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_3PRB_GUARDBAND.ARB",
"4-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1698_QPSK.ARB",
"6-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1702_QPSK.ARB",
"6-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1702_QPSK_2PRB_GUARDBAND.ARB",
"6-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1702_QPSK_3PRB_GUARDBAND.ARB",
"7-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1702_QPSK.ARB",
"8-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK.ARB",
"8-1-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK_1PRB_GUARDBAND.ARB",
"8-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK_2PRB_GUARDBAND.ARB",
"8-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1707_QPSK_3PRB_GUARDBAND.ARB",
"9-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1707_QPSK.ARB",
"16-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_QPSK_METOP.ARB",
"16-1-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_1PRB_GUARDBAND.ARB",
"16-2-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_2PRB_GUARDBAND.ARB",
"16-3-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_3PRB_GUARDBAND.ARB",
"17-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB",
"18-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_PUCCH.ARB",
"19-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_1701_QPSK_METOP_PUCCH.ARB",
"22-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLCP_ALLPUSCH_NONBLANKED.ARB",
"23-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_NONBLANKED.ARB"
]

# waveforms_5MHz = [
# "1-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK.ARB"
# "1-1-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_1PRB_GUARDBAND.ARB"
# "1-2-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_2PRB_GUARDBAND.ARB"
# "1-3-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1698_QPSK_3PRB_GUARDBAND.ARB"
# "3-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLDFT_ALLPUSCH_1698_QPSK.ARB"
# "5-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH1_PRBSET11TO24_5MHZ_VAR_1698.ARB"
# "10-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_QPSK_METOP.ARB"
# "10-1-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_1PRB_GUARDBAND.ARB"
# "10-2-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_2PRB_GUARDBAND.ARB"
# "10-3-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_1701_METOP_QPSK_3PRB_GUARDBAND.ARB"
# "11-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB"
# "12-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH14_PRBSET24_5MHZ_VAR_1701_METOP.ARB"
# "13-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH14_PRBSET23TO24_5MHZ_VAR_1701_METOP.ARB"
# "14-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH14_PRBSET24_INTERASLOTHOPPING_5MHZ_VAR_1701_METOP.ARB"
# "15-PUCCH_FORMAT3_STARTSYMBOL0_SYMBOLLENGTH1_PRBSET11TO24_5MHZ_VAR_1701_METOP.ARB"
# "20-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLCP_ALLPUSCH_QPSK_NONBLANKED.ARB"
# "21-5MHZ_SCS15KHZ_3UES_ALLTTI_ALLDFT_ALLPUSCH_QPSK_NONBLANKED.ARB"
# ]

with RM.open_resource(MXG_RESOURCE_STRING, timeout=2000) as MXG:
    MXG.read_termination = '\n'
    MXG.write_termination = '\n'
    
    # MXG reset/setup
    MXG.write('*IDN?')
    mxg_idn = MXG.read()
    print(f'MXG: {mxg_idn}')

    #RMXG Config
    MXG.write('*RST')
    MXG.write('*CLS')

    MXG.write(':FREQ 1702.5 MHZ')
    freq = MXG.query_ascii_values(':FREQ?')
    # print(f'CF: {freq}')

    MXG.write(':POW -60 DBM')
    power = MXG.query_ascii_values(':POW?')
    # print(f'Power: {power}')

    # Extract waveform names from the response
    for entry in waveforms_15MHz:
        # print(f'setting up now and sending "{entry}"')

        MXG.write(f':RAD:ARB:WAV "{entry}"')
    # MXG.write(':RAD:ARB:WAV "%s"' % ('17-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB'))
    # MXG.write('RAD:ARB:WAV "17-15MHZ_SCS15KHZ_9UES_ALLTTI_ALLDFT_ALLPUSCH_1701_QPSK_METOP.ARB"')
        waveform = MXG.query(':RAD:ARB:WAV?')
        print(f'WFM Configured: {waveform}')

        MXG.write(':RAD:ARB:SCL:RATE 23.04 MHZ')
        sampleClock = MXG.query_ascii_values(':RAD:ARB:SCL:RATE?')
        # print(f'Sample Clock: {sampleClock}')

        if MXG.query('*OPC?') == '1':
            MXG.write(':RAD:ARB 1')
            MXG.write(':OUTP 1')
            time.sleep(2)
            # input('Waiting for user confirmation')
            with RM.open_resource(PXA_RESOURCE_STRING, timeout = 2000) as PXA:
                # PXA reset/setup
                PXA.write('*RST')
                PXA.write('*CLS')
                PXA.write('SYST:DEF SCR')
                pxa_idn = PXA.query('*IDN?')
                print(f'PXA: {pxa_idn}')
                PXA.write("INIT:CONT ON")
                PXA.write('SENS:FREQ:CENT 1702500000')
                PXA.write('FREQ:SPAN 20000000')
                PXA.write('DISP:WIND:TRAC:Y:RLEV -40')
                PXA.write('POW:ATT 0')
                PXA.write('POW:GAIN ON')
                PXA.write('BAND:RES 1000')

                PXA.write(":INST:NSEL 8")
                PXA.write(":CONF:WAV")
                PXA.write(":INIT:CONT OFF")
                PXA.write('SENS:FREQ:CENT 1702500000')
                PXA.write('POW:ATT:AUTO OFF')
                PXA.write('POW:ATT 0')
                PXA.write('DISP:WAV:VIEW:NSEL 1')
                PXA.write('POW:GAIN ON')
                PXA.write('WAV:SRAT 18.75MHz')
                PXA.write('WAV:SWE:TIME 16ms')
                PXA.write('DISP:WAV:VIEW:WIND:TRAC:Y:COUP ON')
                PXA.write(":FORM:BORD SWAP")
                PXA.write(":FORM REAL,32")
        else:
            print("Operation issue")
            break        

    # for entry in waveforms_5MHz:
    #     MXG.write(':FREQ 1702.5 MHZ')
    #     MXG.write(':FREQ?')
    #     MXG.write(':POW -60 DBM')
    #     MXG.write(':POW?')
    #     MXG.write(':RAD:ARB:SCL:RATE 23.04 MHZ')
    #     MXG.write(':RAD:ARB:SCL:RATE?')
    #     MXG.write(f':RAD:ARB:WAV "{entry}"')
    #     MXG.write(':RAD:ARB 1')
    #     MXG.write(':OUTP 1')
    #     pass

