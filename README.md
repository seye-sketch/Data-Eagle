# 🏪 DataWatch: Autonomous BI Agent for Emerging Markets

[![Google Agentic Hackathon](https://img.shields.io/badge/Hackathon-Google%20All%20Things%20Agentic-blue?style=flat-square&logo=google)](https://github.com/seye-sketch/Data-Eagle)
[![Gemini](https://img.shields.io/badge/AI-Gemini%203.5%20Flash-orange?style=flat-square&logo=google-gemini)](https://deepmind.google/technologies/gemini/)
[![Google Sheets](https://img.shields.io/badge/Integration-Google%20Sheets-green?style=flat-square&logo=google-sheets)](https://www.google.com/sheets/about/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

An autonomous business intelligence and anomaly detection agent built using the **Google Agent Development Kit (ADK)** and **Gemini 3.5 Flash**. Designed specifically for the **Google "All Things Agentic" Hackathon (Taskmaster track)**.

---

## 📌 Problem Statement & Project Overview

Imagine **Tunde**, a small business owner in Lagos, Nigeria. Tunde runs **three busy Suya spots** across Lagos (Ikeja, Surulere, and Lekki). He does great business daily but faces significant challenges:
- He **cannot afford** a full-time data analyst or complex BI tools (like Power BI / Tableau enterprise licenses).
- He is constantly busy managing suppliers, staff, and operations, leaving zero time to pore over spreadsheets.
- Critical business events—such as a sudden **99% drop in hourly sales** at Ikeja due to a power outage, or supplier inflation eating his margins—often go unnoticed until it's too late.

### 💡 The Solution: DataWatch
**DataWatch** acts as Tunde's private, autonomous data analyst. It runs quietly in the background on **Cloud Run**, connects directly to his sales spreadsheets, reasons about performance using the advanced cognitive capabilities of **Gemini 3.5 Flash**, and sends him simple, actionable **WhatsApp alerts** and weekly summaries. It brings enterprise-grade intelligence to emerging market entrepreneurs for pennies a day.

---

## 🚀 Key Features

- 🧠 **Gemini-Powered Anomaly Detection:** Uses Gemini 3.5 Flash to intelligently analyze sales patterns, accounting for local contexts (e.g., Nigerian public holidays, heavy rain season, or power grid failures) to separate noise from true business anomalies.
- 📊 **Seamless Google Sheets Integration:** Automatically pulls and syncs transaction records from Google Sheets, using it as a lightweight, free database for the business owner.
- 💬 **Instant WhatsApp Alerts:** When a severe anomaly (e.g., 90%+ sudden revenue drop during peak hours) is detected, DataWatch instantly alerts the owner via WhatsApp with exact numbers and causes.
- 📈 **Weekly Business Reports:** Automatically compiles structured weekly performance reports, charts business trends using Matplotlib, and delivers them directly to the owner.
- 🕒 **Automated Cron Schedule:** Runs on a lightweight, scheduled cron cycle to check sales data hourly/daily, operating with 100% autonomy.

---

## 🏗️ Architecture

DataWatch's lightweight and cost-effective architecture is built on the Google Cloud stack:

```
[ Google Sheets ] ──(Sync)──> [ Python / gspread ]
                                     │
                             (Fetch Sales Data)
                                     ▼
[ Google Cloud Run ] ──> [ Google Agentic SDK (ADK) ]
                                     │
                             (Reason / Detect)
                                     ▼
                        [ Gemini 3.5 Flash Model ]
                                     │
                             (Analyze Anomalies)
                                     ▼
[ WhatsApp Gateway ] <───(Alerts)─── [ DataWatch Agent ]
```

- **Google Agentic SDK (ADK):** Powers the autonomous agent loop, managing tool bindings and memory across runs.
- **Gemini 3.5 Flash:** Provides lightning-fast, high-quality reasoning to analyze sales data and formulate context-aware explanations.
- **Google Sheets API:** Serves as the free, accessible data entry and storage layer for the merchant.
- **Cloud Run & Cron:** Hosts the lightweight execution environment, triggered autonomously every hour/day.

---

## 🔄 How It Works

1. **Data Ingestion (90-Day History):** DataWatch pulls the last 90 days of transactions from Google Sheets to establish a statistical baseline for each branch (Ikeja, Surulere, Lekki).
2. **Daily Aggregation:** Each day/hour, sales are aggregated and analyzed.
3. **Cognitive Reasoning:** Gemini 3.5 Flash compares the fresh hourly data against historical baselines, factoring in:
   - Time of day (e.g., peak lunch/dinner hours vs. morning lulls).
   - Historical branch variance.
   - Known local anomalies (power grid failure notes, public holidays).
4. **Actionable Outputs:**
   - **Severe Anomaly:** Fires an instant, high-priority WhatsApp alert.
   - **Daily/Weekly Recap:** Consolidates a structured weekly report, renders a trend visualization, and sends it directly to the owner.

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.11+
- A Google Cloud Project with the **Sheets API**, **Drive API**, and **Vertex AI / Gemini API** enabled.
- A WhatsApp API / Gateway account (or Sandbox) for alerts.

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/seye-sketch/Data-Eagle.git
cd Data-Eagle
pip install -r requirements.txt
```

### 2. Authentication Setup
- Create a **Service Account** in the Google Cloud Console.
- Download the credentials file and save it as **`credentials.json`** in the project root directory.
- Share your Google Sheet with the Service Account email.

### 3. Environment Variables
Create a `.env` file in `datawatch_agent/.env` (and/or in the root) with the following values:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
WHATSAPP_ENABLED=true
WHATSAPP_HOME_CHANNEL=your_whatsapp_channel_id
```

### 4. Running the Agent
Run the simulated daily data generator and scheduled monitor tasks:
```bash
# Generate simulated historical sales data
python3 generate_data.py

# Check for severe anomalies (run on cron)
python3 check_severe.py

# Run the weekly business intelligence recap
python3 run_weekly.py
```

---

## 📂 Project Structure

```directory
datawatch/
├── datawatch_agent/
│   └── agent.py                # Main Google ADK Agent definition and tool bindings
├── check_severe.py             # Scheduled monitor to check for critical drops (WhatsApp trigger)
├── generate_data.py            # Simulates 90-day transaction history for Suya spots
├── run_weekly.py               # Handles compiling and sending the weekly recap
├── .gitignore                  # Git ignore configurations
└── README.md                   # Project documentation
```

---

## 🛠️ Built With

- **[Google Agentic SDK (ADK)](https://github.com/google/agentic-sdk):** Autonomous agent loop, scheduling, and tool binding.
- **[Gemini 3.5 Flash](https://deepmind.google/technologies/gemini/):** High-throughput reasoning, data analysis, and report generation.
- **[Google Sheets API (via gspread)](https://github.com/burnash/gspread):** Cloud data synchronization.
- **[Matplotlib](https://matplotlib.org/):** Business intelligence chart and trend rendering.
- **[Flask](https://flask.palletsprojects.com/):** Optional web UI/webhook service for Cloud Run routing.
- **[Cloud Run](https://cloud.google.com/run):** Fully managed, serverless execution platform.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Built with passion for emerging market merchants at the Google All Things Agentic Hackathon.* 🇳🇬🔥
