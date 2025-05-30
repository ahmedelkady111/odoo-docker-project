import requests
import hmac
import hashlib
import json
import os

ODOO_WEBHOOK_URL = "https://your-odoo-domain.com/github/webhook"
GITHUB_WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]

payload = {
    "branch": "main",
    "user_email": "user@example.com",
    "task_id": 123  # Set this as needed
}
data = json.dumps(payload).encode("utf-8")
signature = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), data, hashlib.sha256).hexdigest()
headers = {
    "Content-Type": "application/json",
    "X-Hub-Signature-256": f"sha256={signature}"
}
response = requests.post(ODOO_WEBHOOK_URL, data=data, headers=headers)
print(response.status_code, response.text)