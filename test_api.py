import requests

url = "http://127.0.0.1:5000/detect?use_sahi=true&conf=0.25"
files = {'image': open('1.png', 'rb')}

try:
    response = requests.post(url, files=files)
    print("API Response Status Code:", response.status_code)
    data = response.json()
    print("Total Detections:", data.get('total_detections'))
    print("Breakdown:", data.get('breakdown'))
    if data.get('detections'):
        print("Sample Detection:", data['detections'][0])
except Exception as e:
    print("API Test Error:", str(e))