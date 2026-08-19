import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gspread
from google.oauth2.service_account import Credentials
from google import genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")

def get_sheet_data():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open("Datawatch Sales Data").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def build_business_profile(df):
    profile = "DATAWATCH BUSINESS PROFILE\n"
    profile += "Branches: Ikeja, Surulere, Lekki\n"
    profile += "Business hours: 8am-7pm daily\n\n"
    for branch in ["Ikeja", "Surulere", "Lekki"]:
        b = df[df["branch"] == branch]
        profile += f"{branch} branch:\n"
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            day_avg = b[b["day"] == day]["sales"].mean()
            if pd.notna(day_avg):
                profile += f"  {day} average: ₦{day_avg:,.0f}/hr\n"
        peak = b.groupby("hour")["sales"].mean().idxmax()
        profile += f"  Peak hour: {peak}:00\n\n"
    return profile

def analyze_sales():
    df = get_sheet_data()
    today_str = df["date"].max()
    history_df = df[df["date"] < today_str]
    today_df = df[df["date"] == today_str]

    profile = build_business_profile(history_df)
    today_text = today_df[["hour", "branch", "sales"]].to_string(index=False)

    memory = load_memory()
    memory_text = ""
    if memory:
        memory_text = "\nOWNER NOTES:\n"
        for key, explanation in memory.items():
            memory_text += f"- {explanation}\n"
        memory_text += "\nTake these notes into account before flagging anomalies.\n"

    prompt = f"""You are a business intelligence assistant analyzing sales data for a Nigerian suya business with 3 branches.

Note: Nigeria has public holidays where sales drop significantly. Consider this before flagging low sales as anomalies.

{profile}
{memory_text}
TODAY'S SALES ({today_str}):
{today_text}

Identify any anomalies in today's sales. For each anomaly state the branch, hour, sales amount, and why it is unusual. Be concise."""

    ai_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    response = ai_client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    branch_totals = {
        b: int(df[df["branch"] == b]["sales"].sum())
        for b in ["Ikeja", "Surulere", "Lekki"]
    }

    return {
        "total_records": len(df),
        "today_date": today_str,
        "gemini_analysis": response.text,
        "branch_totals": branch_totals
    }

def generate_chart():
    df = get_sheet_data()
    today_str = df["date"].max()
    history_df = df[df["date"] < today_str]
    today_df = df[df["date"] == today_str]

    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    branches = ["Ikeja", "Surulere", "Lekki"]

    for i, branch in enumerate(branches):
        hist = history_df[history_df["branch"] == branch].groupby("hour")["sales"].mean()
        today = today_df[today_df["branch"] == branch].set_index("hour")["sales"]
        axes[i].plot(hist.index, hist.values, color="steelblue", linewidth=1.5, label="Historical avg")
        axes[i].plot(today.index, today.values, color="orange", linewidth=1.5, label="Today")
        axes[i].set_title(f"{branch} Branch")
        axes[i].set_ylabel("Sales (₦)")
        axes[i].legend()

    plt.suptitle("DataWatch — Today vs Historical Average", fontsize=14, fontweight="bold")
    plt.tight_layout()
    chart_path = "/tmp/sales_report.png"
    plt.savefig(chart_path, dpi=150)
    plt.close()
    return chart_path
