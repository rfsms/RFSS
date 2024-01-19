from http.client import http
import json

def get_current_AzEl():
    conn = http.client.HTTPConnection("192.168.4.1", 80)
    conn.request("GET", "/min")
    response = conn.getresponse()
    data = json.loads(response.read())
    conn.close()
    return round(data['az']), round(data['el'])

azimuth, elevation = get_current_AzEl()
print(f"AZ_{azimuth}_EL_{elevation}")