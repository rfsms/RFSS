# RFSS
NOAA - RF Survey System: [rsAutomated-StartStop.py](./rsAutomated-StartStop.py)

This code is intended to be run on the RF Survey System (RFSS) located at different earth stations to evaluate RF Interference (RFI) anomolies that may exist in the environment prior to and during a meteorological satellite pass.

Instruments for automation include the R&S FSV3000 Spectrum Analyzer configured for both Spectrum and IQ sweeps to measure prior to and during a satellite pass.  

Currently, this is designed to capture 16ms IQ samples every 8 seconds while a Griddy antenna attached to Yaesu G5500 rotor tracks the satellite across the sky.  The Yaesu and schedule is controlled by CSN Technologies S.A.T Controller.  Once the data has been captured by the FSV, the RFSS grabs all the IQ data and wipes the Spectrum Analyzer user folder.  Then RFSS  "tgz's" them all up and ships them to an EC2 instance.  

All traffic between EC2 and RFSS is over a WireGuard PTP VPN and private/public keys are used for SCP connections.

![Alt text](image.png)

* Future modification include only scanning between -10* and +10* elevation in a 360* azimuthal rotation.
* Additionally, more functionality will be incorporated to include autonomous scheduling so a static start/stop time does not need to be defined.
* Lastly the code will include usage if an Ettus x310 SDR relacing the FSV Spectrum Analyer.