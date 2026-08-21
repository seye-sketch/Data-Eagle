import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("Datawatch Sales Data").sheet1

branch = sys.argv[1] if len(sys.argv) > 1 else "Lekki"
hour = int(sys.argv[2]) if len(sys.argv) > 2 else datetime.now().hour
sales = int(sys.argv[3]) if len(sys.argv) > 3 else 200

today = datetime.now()
day_name = today.strftime("%A")
date_str = today.strftime("%Y-%m-%d")

row = [date_str, day_name, hour, branch, sales]
sheet.append_row(row)

print(f"✅ Anomaly injected:")
print(f"   Branch: {branch}")
print(f"   Date: {date_str} ({day_name})")
print(f"   Hour: {hour}:00")
print(f"   Sales: ₦{sales:,}")
