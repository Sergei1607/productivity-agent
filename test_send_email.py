import os
from dotenv import load_dotenv
import requests

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

response = requests.post(
    "https://api.resend.com/emails",
    headers={
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "from": "onboarding@resend.dev",
        "to": "sergei.redondo@gmail.com",
        "subject": "Test from productivity agent",
        "text": "This is a standalone test of the send_briefing_email tool, before wiring it into the agent loop.",
    },
)

print(response.status_code)
print(response.json())