import pandas as pd
from datetime import datetime
import json

# Path to your CSV file
file_path = '/home/noaa_gms/RFSS/toDemod/2023_12_20/results/results.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Replace NaN values in DataFrame with None
# df = df.where(pd.notnull(df), None)

# Transform DataFrame into the specified JSON structure
events = []
for _, row in df.iterrows():
    if row["PCI"] != -1:  # Check if PCI is not -1
        event = {
            "PCI": row["PCI"],
            "_id": "",
            "beam": "upper hemisphere scanning",
            "carrierID": "Unknown",
            "cellID": "Unknown",
            "eNodeB": "Unknown",
            "elevationAngle": 0,
            "elevationAngleUnits": "degrees",
            "eventID": row["timestamp"],
            "headingAzimuth": "",
            "headingAzimuthUnits": "degrees",
            "inverseAxialRatio": "",
            "labels": "",
            "locationLat": "",
            "locationLatUnits": "degrees",
            "locationLon": "",
            "locationLonUnits": "degrees",
            "maxBandwidth": "",
            "maxBandwidthUnits": "",
            "maxFrequency": "",
            "maxFrequencyUnits": "MHz",
            "maxPower": row["SNR(dB)"] if row["SNR(dB)"] != "" else "",
            "maxPowerUnits": "dBm",
            "mode": "Operational",
            "notifyCarrier": "",
            "remoteID": 1003,
            "severityLevel": "warning",
            "signalType": row["5G/LTE"],
            "tiltAngle": "NA",
            "tiltAngleUnits": "degrees",
            "timestamp": datetime.now().isoformat()
        }
        events.append(event)

# Convert to JSON
json_data = json.dumps({"events": events}, indent=4)

# Print the JSON data
print(json_data)
