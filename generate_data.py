import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import random

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("Datawatch Sales Data").sheet1

branches = ["Ikeja", "Surulere", "Lekki"]
business_hours = range(8, 20)

def generate_day(date):
    random.seed(date.toordinal())
    np.random.seed(date.toordinal())
    rows = []
    day_of_week = date.strftime("%A")
    for branch in branches:
        for hour in business_hours:
            if day_of_week in ["Saturday", "Sunday"]:
                base = random.randint(40000, 80000)
            elif day_of_week == "Monday":
                base = random.randint(10000, 25000)
            else:
                base = random.randint(20000, 50000)
            if hour in [12, 18]:
                base = int(base * 1.4)
            rows.append({
                "date": date.strftime("%Y-%m-%d"),
                "day": day_of_week,
                "hour": hour,
                "branch": branch,
                "sales": base
            })
    return rows

# 90 days of history ending yesterday (Aug 15)
print("Clearing sheet and uploading fresh data...")
today = datetime(2026, 8, 16)
start_date = today - timedelta(days=90)

all_rows = []
for d in range(90):
    all_rows.extend(generate_day(start_date + timedelta(days=d)))

# Plant anomalies in history
for row in all_rows:
    if row["branch"] == "Surulere" and row["date"] == "2026-06-04" and row["hour"] == 14:
        row["sales"] = 500
    if row["branch"] == "Lekki" and row["date"] == "2026-06-10" and row["hour"] == 8:
        row["sales"] = 0

df = pd.DataFrame(all_rows)
sheet.clear()
sheet.append_row(df.columns.tolist())
sheet.append_rows(df.values.tolist())
print(f"Uploaded {len(df)} rows of history (May 18 - Aug 15)")

# Add today (Aug 16) with planted anomaly
print("Adding today's data (Aug 16)...")
today_rows = generate_day(today)
for row in today_rows:
    if row["branch"] == "Ikeja" and row["hour"] == 12:
        row["sales"] = 300

sheet.append_rows([[r["date"], r["day"], r["hour"], r["branch"], r["sales"]] for r in today_rows])
print(f"Added {len(today_rows)} rows for today with Ikeja 12pm crash (₦300)")
print("Done!")
