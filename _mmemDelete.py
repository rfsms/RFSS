from RsInstrument import *

resource_string_1 = 'TCPIP::192.168.1.101::hislip0'
option_string_force_rs_visa = 'SelectVisa=rs'
RsInstrument.assert_minimum_version('1.53.0')

instr = RsInstrument(resource_string_1, False, False, option_string_force_rs_visa) #(Resource, ID Query, Reset, Options)

# Switch ON logging to the console for troubleshooting SpecAn config issues
instr.logger.log_to_console = True
instr.logger.mode = LoggingMode.On

# Set the current directory
instr.write('MMEM:DEL "c:\\R_S\\Instr\\user\\RFSS\\*"')

instr.reset()