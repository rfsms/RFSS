import requests

url = "https://ec2-52-61-173-155.us-gov-west-1.compute.amazonaws.com/api/data"

data = {
    "events": [
        {
            "PCI": 854, 
            "_id": "65550941cfc51ffcb40a37ff", 
            "beam": "upper hemisphere scanning", 
            "carrierID": "Unknown", 
            "cellID": "Unknown", 
            "eNodeB": "Unknown", 
            "elevationAngle": 0, 
            "elevationAngleUnits": "degrees", 
            "eventID": "1-2023319180817005S001", 
            "headingAzimuth": 9.9, 
            "headingAzimuthUnits": "degrees", 
            "inverseAxialRatio": -0.19, 
            "labels": ["1-1-2023319175803027S001"], 
            "locationLat": 40.131186, 
            "locationLatUnits": "degrees", 
            "locationLon": -105.240135, 
            "locationLonUnits": "degrees", 
            "maxBandwidth": 180, 
            "maxBandwidthUnits": "kHz", 
            "maxFrequency": 1702.492, 
            "maxFrequencyUnits": "MHz", 
            "maxPower": -120.1, 
            "maxPowerUnits": "dBm / 180kHz", 
            "mode": "Operational", 
            "notifyCarrier": True, 
            "remoteID": 1003, 
            "severityLevel": "warning", 
            "signalType": "5G NR", 
            "tiltAngle": 18.2, 
            "tiltAngleUnits": "degrees", 
            "timestamp": "2023-11-15T18:08:17.005Z"
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