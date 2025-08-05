import requests
import base64

client_id = 'RKB-admin-81'
client_secret = 'openemras859944@'

auth_str = f'{client_id}:{client_secret}'
auth_bytes = auth_str.encode('utf-8')
auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

headers = {
          "Content-Type": "application/x-www-form-urlencoded",
          "Authorization" : f"Basic {auth_base64}"
          }

data = {
    "grant_type" : "authorization_code"
}

auth_path = "http://localhost/openemr/oauth2/default/token" 

response = requests.post(auth_path, data=data, headers=headers)

# 결과 확인
if response.status_code == 200:
    token = response.json().get("token")
    print("✅ Access token:", token)
else:
    print("❌ Login failed:", response.status_code)
    print(response.text)