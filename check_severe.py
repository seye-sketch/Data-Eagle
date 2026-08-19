import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import subprocess

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("Datawatch Sales Data").sheet1
df = pd.DataFrame(sheet.get_all_records())

today_str = df["date"].max()
history_df = df[df["date"] < today_str]
today_df = df[df["date"] == today_str]

severe = []

for branch in ["Ikeja", "Surulere", "Lekki"]:
    branch_history = history_df[history_df["branch"] == branch]
    branch_today = today_df[today_df["branch"] == branch]

    for _, row in branch_today.iterrows():
        hour = row["hour"]
        sales = row["sales"]
        hour_avg = branch_history[branch_history["hour"] == hour]["sales"].mean()

        if pd.isna(hour_avg):
            continue

        drop_pct = (hour_avg - sales) / hour_avg * 100

        if sales == 0 or drop_pct >= 90:
            severe.append({
                "branch": branch,
                "hour": hour,
                "sales": sales,
                "expected": round(hour_avg),
                "drop_pct": round(drop_pct)
            })

if severe:
    alert = "🚨 *SEVERE ANOMALY ALERT*\n"
    alert += f"📅 {today_str}\n\n"
    for s in severe:
        alert += f"• {s['branch']} — {s['hour']}:00\n"
        alert += f"  Sales: ₦{s['sales']:,} | Expected: ₦{s['expected']:,}\n"
        alert += f"  Drop: {s['drop_pct']}% below normal\n\n"
    alert += "⚡ Immediate attention required."

    print(alert)

    # Send to WhatsApp
    subprocess.run(["hermes", "send", "--to", "whatsapp:Seye", alert])
    print("Alert sent to WhatsApp!")

    with open("/home/seyealadekomo/datawatch/severe_alert.txt", "w") as f:
        f.write(alert)
else:
    print(f"No severe anomalies detected for {today_str}. All clear.")
