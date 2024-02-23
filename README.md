# RFSS (RF Survey System)
## Overview

This code is intended to be run on the RF Survey System (RFSS) located at different earth stations to evaluate RF Interference (RFI) anomolies that may exist in the environment prior to and during a meteorological satellite pass.  

The system utilizes either a R&S FSV3000 or Keysight PXA N9030B spectrum analyzer's for Spectrum and IQ sweeps to measure prior to and during a satellite pass. This code requires rsInstrument and pyVisa. Both can be installed via requiremetns.txt.  Additionally, rsvisa will need to be installed from the Tools folder or can be downloaded directly from R&S.

Additionally, you will need to ensure you are synced in time.  Preferred way is with systemd-timesyncd and NTP=time.nist.gov in /etc/systemd/timsyncd.conf.

Currently, the system is designed to capture 160ms IQ samples every 6-8 seconds while a Griddy antenna attached to Yaesu G5500 rotor tracks the satellite across the sky.  The Yaesu and schedule is controlled by CSN Technologies S.A.T Controller.  All data captured from spectrum analyzer is immediately saved to local machine during pass.   


![Alt text](image.png)

## Repository Structure

* RFSS.py: Main service script, handling initialization, configuration, operation, and communication.
* RFSS_FSV.py/RFSS_PXA.py: Scripts for autonomous operation with R&S FSV or Keysight PXA instruments.
* Dashboard/: Contains the web dashboard for updates and monitoring.
* Tools/: Includes utilities like tleUpdate.py for TLE data updates and other various tools
.   
## Future Updates
* Modification to only scanning between -10* and +10* elevation in a 360* azimuthal rotation.
* Add additional scan data from SAT controller, like AZ/EL/voltage, etc.

## Setup and Operation:

* A service is created in `/etc/systemd/system/RFSS.service` to run the RFSS server 
    ```
    [Unit]
    Description=RFSS service after multi-user target
    After=network.target

    [Service]
    Type=simple
    ExecStart=/usr/bin/python3 /home/noaa_gms/RFSS/RFSS.py RFSS_PXA
    Restart=on-failure
    User=noaa_gms
    Group=noaa_gms

    [Install]
    WantedBy=multi-user.target

* A service is created in `/etc/systemd/system/gunicorn.service` to run the webservice as an eventlet
    ```
    [Unit]
    Description=gunicorn daemon
    After=network.target

    [Service]
    User=noaa_gms
    Group=noaa_gms
    WorkingDirectory=/home/noaa_gms/RFSS/Dashboard/
    ExecStart=/usr/local/bin/gunicorn -k eventlet -w 1 -b :8080 app:app
    Restart=always

    [Install]
    WantedBy=multi-user.target  

* Reload systemd with `sudo systemctl daemon-reload`
* Enable and start the service with `sudo systemctl enable RFSS`
* You can then use normal systemd commands to check status, restart, etc. as normal.

## Logging

* To check current satellite schedule you can go to FQDN:8080 to reach the Dashboard
* For RFSS logs: `/home/noaa_gms/RFSS/RFSS_SA.log`

## Code modification:
* If there is a need to change any portion of the code, you simply need to restart the RFSS service with `sudo systemctl restart RFSS.service` and code will start automatically from RFSS, while preserving current daily schedule.


