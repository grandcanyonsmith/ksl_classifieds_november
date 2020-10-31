import requests

payload = {"name": "canyon"}
r = requests.post('https://hooks.zapier.com/hooks/catch/1739571/oq5s6rr/', data=payload)

print(r.text)