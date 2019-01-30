import requests

url = "http://192.168.170.112:4000/data"
message = {"data": True}

requests.post(url, data=message)
