# RFSS
NOAA - RF Survey System -- rsAutonomous.py

(rsAutomated-StartStop.py can be used to manually schedule recording)

This code is intended to be run on the RF Survey System (RFSS) located at different earth stations to evaluate RF Interference (RFI) anomolies that may exist in the environment prior to and during a meteorological satellite pass.  

Instruments for automation include the R&S FSV3000 Spectrum Analyzer configured for both Spectrum and IQ sweeps to measure prior to and during a satellite pass. Due to instrument usage, this code requires both rsInstrument and rsVisa.  rsInstrument can be installed via requirements.txt and rsVisa can be downloaded directly from R&S or from the Tools folder.

Additionally, you will need to ensure you are synced in time.  Preferred way is with systemd-timesyncd and NTP=time.nist.gov in /etc/systemd/timsyncd.conf.

Currently, this is designed to capture 16ms IQ samples every 8 seconds while a Griddy antenna attached to Yaesu G5500 rotor tracks the satellite across the sky.  The Yaesu and schedule is controlled by CSN Technologies S.A.T Controller.  Once the data has been captured by the FSV, the RFSS grabs all the IQ data and wipes the Spectrum Analyzer user folder.  Then RFSS "tgz's" them all up in the Received folder and ships them to an EC2 instance, then deletes all data from Received.  

All traffic between EC2 and RFSS is over a WireGuard based PTP VPN and public keys are used for SCP connections.

![Alt text](image.png)

* Future modification includes only scanning between -10* and +10* elevation in a 360* azimuthal rotation.
* ~~Additionally, more functionality will be incorporated to include autonomous scheduling so a static start/stop time does not need to be defined.~~
* Lastly the code will include usage if an Ettus x310 SDR relacing the FSV Spectrum Analyer.

NOTE:
If SCP is removed and rsync is used instead, ensure that:
* rsyncUpload.sh script is moved to `/usr/local/bin`.
* A service is created in `/etc/systemd/system/rsyncUpload.service`
    ```[Unit]
    Description=Starts the RFSS rsync service after multi-user target
    After=network.target

    [Service]
    Type=simple
    ExecStart=/usr/local/bin/rsyncUpload.sh
    Restart=on-failure
    User=noaa_gms
    Group=noaa_gms

    [Install]
    WantedBy=multi-user.target
* Reload systemd with `sudo systemctl daemon-reload`
* Enable and start the service with `sudo systemctl enable {RFSS/rsyncUpload}`
/`sudo systemctl start {RFSS/rsyncUpload}`
* you can then use normal systemd commands to check status, restart, etc. as normal.
