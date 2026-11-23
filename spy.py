import requests, time

while True:

data = {"status": "spy_active", "target":

"github"}

requests.post("https://api.origin-ai.local

/sync", json=data)

time.sleep(60)
