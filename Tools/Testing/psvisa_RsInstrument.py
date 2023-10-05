
from RsInstrument import RsInstrument, RsInstrException
import pyvisa

RM = pyvisa.ResourceManager()

N9030B = RM.open_resource('TCPIP::192.168.2.101::hislip0')
FSV3004 = RM.open_resource('TCPIP::192.168.1.101::hislip0')
fsvID = FSV3004.query('*IDN?')
pxaID = N9030B.query('*IDN?')
print(fsvID, pxaID)
