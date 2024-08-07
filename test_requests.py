import requests

url = "http://127.0.0.1:5005/influfun"

data = {
    "url": "https://campaignxxxxxxxxxx.com/xxxxxxxxxxxxxxx",
    "username": "IoT_Data99",
    "budget": 150000
}

response = requests.post(url, json=data)

print(response.json())