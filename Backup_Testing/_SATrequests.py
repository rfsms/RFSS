import requests
import time

def fetch_data_from_url(satTracker: str) -> dict:
    """Fetches data from the specified URL and returns it as a dictionary."""
    response = requests.get(satTracker)
    response.raise_for_status()
    return response.json()

def extract_and_round(data: dict, key: str) -> int:
    """Extracts a value from the dictionary and rounds it to a whole number."""
    return round(data.get(key, 0))

def main():
    satTracker = "http://192.168.4.1/track"
    data = fetch_data_from_url(satTracker)

    az = extract_and_round(data, 'az')
    el = extract_and_round(data, 'el')

    print(f"Azimuth (az): {az}°")
    print(f"Elevation (el): {el}°")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(5)