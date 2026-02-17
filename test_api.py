
import requests

url = "http://localhost:8000/api/process-resume"
files = {'file': ('test.pdf', b'dummy content', 'application/pdf')}

try:
    response = requests.post(url, files=files)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Error:", e)
