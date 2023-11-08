import subprocess
from datetime import datetime, timedelta
import time
import logging
import requests

# Reset the Root Logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Setup logging
logging.basicConfig(filename='/home/noaa_gms/RFSS/RFSS_SA.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def analyze_results(yesterday):
    results_file_path = f"/home/noaa_gms/RFSS/toDemod/{yesterday}/results/results.txt"
    total_count = 0
    pci_found_count = 0

    try:
        with open(results_file_path, 'r') as file:
            for line in file:
                total_count += 1
                if not line.strip().endswith("-1"):
                    pci_found_count += 1
    except FileNotFoundError:
        logging.info("IQ Processing Results file not found.")

    return total_count, pci_found_count

def get_machine_id():
    with open('/etc/machine-id', 'r') as file:
        return file.read().strip()
    
def send_notification(total_iq, pci_found):
    machine_id = get_machine_id()
    url = f'https://ntfy.sh/{machine_id}'
    message = f"Total IQ files processed: {total_iq}, PCI found in: {pci_found} files."
    data = {'message': message}
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.status_code
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while sending notification: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"Connection error occurred while sending notification: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"Timeout error occurred while sending notification: {timeout_err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"An error occurred while sending notification: {err}")
    return None

def run_script():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y_%m_%d')
    logging.info(f"IQ Processing started for {yesterday} folder")

    command = f"/home/noaa_gms/Downloads/Both_vd6/run_RFSS_classifyidentifyPCI_15MHz_vd3.sh /usr/local/MATLAB/MATLAB_Runtime/R2023a /home/noaa_gms/RFSS/toDemod/{yesterday}/ /home/noaa_gms/RFSS/toDemod/{yesterday}/results/"
    process = subprocess.Popen(command, shell=True)

    # Define maximum runtime (e.g., 23 hours)
    max_runtime_seconds = 12 * 3600

    # Monitor the process
    for _ in range(max_runtime_seconds):
        if process.poll() is not None:
            # IQ Processing in progress...
            break
        time.sleep(1)
    else:
        # Process is still running after max_runtime_seconds, terminate it
        logging.info("Sending SIGTERM to IQ process")
        process.terminate()

        # Give it a few seconds to terminate
        time.sleep(5)

        # If the process is still running, kill it
        if process.poll() is None:  # if poll() returns None, the process is still running
            logging.info("Terminating IQ process failed -- Killing instead.")
            process.kill()
        else:
            logging.info("IQ Processs successfully terminated with process.terminate()")

    # Analyze results
    total_iq, pci_found = analyze_results(yesterday)
    logging.info(f"Total IQ files processed: {total_iq}, PCI found in: {pci_found} files.")
    send_notification(total_iq, pci_found)  # send curl ntfy here.....
    logging.info(f"IQ Processing terminated as expected after running for {max_runtime_seconds / 3600} hours.")

run_script()