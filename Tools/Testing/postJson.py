import requests

url = "https://ec2-52-61-173-155.us-gov-west-1.compute.amazonaws.com/api/data"

data = {
    "events": [
        {
            "PCI": 402,
            "_id": 0,
            "beam": "upper hemisphere scanning",
            "carrierID": "Unknown",
            "cellID": "Unknown",
            "eNodeB": "Unknown",
            "elevationAngle": 0,
            "elevationAngleUnits": "degrees",
            "eventID": "20231128_180501.mat_1",
            "headingAzimuth": 0,
            "headingAzimuthUnits": "degrees",
            "inverseAxialRatio": 0,
            "labels": "None",
            "locationLat": 0,
            "locationLatUnits": "degrees",
            "locationLon": 0,
            "locationLonUnits": "degrees",
            "maxBandwidth": 0,
            "maxBandwidthUnits": "kHz",
            "maxFrequency": 0,
            "maxFrequencyUnits": "MHz",
            "maxPower": 31.6182,
            "maxPowerUnits": "dBm",
            "mode": "Operational",
            "notifyCarrier": None,
            "remoteID": 1003,
            "severityLevel": "warning",
            "signalType": "5G",
            "tiltAngle": 0,
            "tiltAngleUnits": "degrees",
            "timestamp": "2023-12-21T18:54:49.732Z"
        }
    ]
}

try:
    print("Sending POST request to the URL...")
    response = requests.post(url, json=data, verify=False)
    print("Request sent successfully.")

    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("Response:", response.text)
    else:
        print("Error response from server:", response.text)
except requests.exceptions.RequestException as e:
    print("An error occurred during the request.")
    print("Error details:", str(e))