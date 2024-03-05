import requests
import logging
from time import sleep

# Reset the Root Logger - this section is used to reset the root logger and then apply below configuration
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

# Function to send requests and check response
def make_request(url, data=None, method='POST'):
    try:
        if method == 'POST':
            response = requests.post(url, data=data)
        elif method == 'GET':
            response = requests.get(url)
        else:
            logging.error(f"Unsupported method: {method}")
            return False
        
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logging.info(f"SCHED: Request to {url} succeeded with method {method}.")
        return True
    except requests.exceptions.HTTPError as errh:
        logging.error(f"SCHED: HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"SCHED: Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"SCHED: Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"SCHED: Oops - something Else {err}")
    return False

# URLs and data for the requests
pause_url = "http://localhost:8080/pause_schedule"
pre_set_az_url = "http://192.168.4.1/cmd?a=P|0|0|"
set_az_url = "http://localhost:8080/set_az"
set_az_data = {
    "startingAZ": 0,
    "endingAZ": 360,
    "centerFreq": 1702.5,
    "span": 85,
    "points": 1001,
    "iqOption": "off",
    "bandConfig": "AWS1"
}

# Pause the schedule
if make_request(pause_url, method='POST'):
    logging.info("Schedule paused. Proceeding with pre-set azimuth command.")
    
    # Send pre-set azimuth command and assume it's a GET request
    if make_request(pre_set_az_url, method='GET'):
        logging.info("SCHED: Pre-set azimuth command succeeded. Waiting for 1 minute before executing scan.")
        sleep(10)  # Wait for 1 minute
        
        # Set rotor azimuth
        if not make_request(set_az_url, data=set_az_data, method='POST'):
            logging.error("SCHED: Failed to set rotor azimuth due to an error in POST request.")
        else:
            logging.info("SCHED: Rotor azimuth set successfully.")
    else:
        logging.error("SCHED: Failed to send pre-set azimuth command.")
else:
    logging.error("SCHED: Failed to pause schedule due to an error in POST request.")
