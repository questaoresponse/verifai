import requests
print(requests.post("http://127.0.0.1:12345/webhook", json={"sla":"eisiaojsosdhdohdo"}).content)