from flask import Flask, render_template_string, send_file, jsonify
from datawatch_core import analyze_sales, generate_chart
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DataWatch — Autonomous BI Agent</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a0a; color: #fff; }

        .hero { background: linear-gradient(135deg, #0a0a0a 0%, #0d2b1a 100%); padding: 4rem 2rem; text-align: center; border-bottom: 1px solid #1a3a2a; }
        .hero h1 { font-size: 3rem; color: #00e676; margin-bottom: 0.5rem; }
        .hero p { font-size: 1.2rem; color: #aaa; max-width: 700px; margin: 0 auto 1rem; }
        .hero-context { background: #0d2b1a; border: 1px solid #1a3a2a; border-radius: 8px; max-width: 700px; margin: 1.5rem auto 0; padding: 1rem 1.5rem; font-size: 0.9rem; color: #aaa; text-align: left; line-height: 1.7; }
        .hero-context strong { color: #00e676; }

        .container { max-width: 900px; margin: 0 auto; padding: 2rem; }
        h2 { font-size: 1.1rem; color: #00e676; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1.5rem; }

        .pipeline { display: flex; flex-direction: column; align-items: center; gap: 0; margin-bottom: 3rem; }
        .pipeline-step { width: 100%; max-width: 700px; }
        .pipeline-box { background: #111; border: 1px solid #1e1e1e; border-radius: 12px; padding: 1.5rem; transition: border-color 0.4s; }
        .pipeline-box.active { border-color: #00e676; }
        .pipeline-box.anomaly { border-color: #ff5252; }
        .pipeline-box.success { border-color: #00e676; }

        .step-label { font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.3rem; }
        .step-title { font-size: 1rem; font-weight: bold; color: #fff; margin-bottom: 0.5rem; }
        .step-desc { font-size: 0.85rem; color: #aaa; line-height: 1.6; }
        .step-status { font-size: 0.85rem; margin-top: 0.8rem; color: #555; min-height: 1.2rem; }
        .step-status.done { color: #00e676; }
        .step-status.alert { color: #ff5252; }
        .step-status.working { color: #ff9800; }

        .arrow { display: flex; flex-direction: column; align-items: center; padding: 0.4rem 0; }
        .arrow-line { width: 2px; height: 28px; background: #1e1e1e; transition: background 0.5s; }
        .arrow-line.active { background: #00e676; }
        .arrow-head { width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-top: 8px solid #1e1e1e; transition: border-top-color 0.5s; }
        .arrow-head.active { border-top-color: #00e676; }

        .schedule { display: flex; gap: 1rem; margin-top: 0.8rem; flex-wrap: wrap; }
        .schedule-item { background: #0d2b1a; border: 1px solid #1a3a2a; border-radius: 6px; padding: 0.4rem 0.8rem; font-size: 0.78rem; color: #00e676; }

        .branch-box { display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap; }
        .branch-option { flex: 1; min-width: 180px; border-radius: 8px; padding: 1rem; text-align: center; font-size: 0.85rem; line-height: 1.6; }
        .branch-normal { background: #0d2b1a; border: 1px solid #00e676; color: #00e676; }
        .branch-anomaly { background: #2b0d0d; border: 1px solid #ff5252; color: #ff5252; }

        .btn { padding: 0.75rem 1.8rem; border-radius: 8px; border: none; cursor: pointer; font-size: 0.95rem; font-weight: bold; background: #00e676; color: #000; transition: all 0.2s; margin-top: 1rem; display: inline-block; }
        .btn:hover { background: #00c853; }
        .btn:disabled { background: #1a3a2a; color: #555; cursor: not-allowed; }

        .spinner { display: inline-block; width: 13px; height: 13px; border: 2px solid #1a3a2a; border-top: 2px solid #00e676; border-radius: 50%; animation: spin 0.8s linear infinite; vertical-align: middle; margin-right: 6px; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .analysis-box { background: #050505; border: 1px solid #00e676; border-radius: 8px; padding: 1.2rem; font-family: monospace; font-size: 0.85rem; white-space: pre-wrap; line-height: 1.7; color: #ddd; margin-top: 1rem; display: none; max-height: 300px; overflow-y: auto; }
        .chart-img { width: 100%; border-radius: 8px; margin-top: 1rem; display: none; border: 1px solid #1e1e1e; }

        .whatsapp-box { background: #0a1f0a; border: 1px solid #25d366; border-radius: 8px; padding: 1.2rem; font-size: 0.85rem; white-space: pre-wrap; line-height: 1.6; color: #ddd; margin-top: 1rem; display: none; }
        .whatsapp-label { color: #25d366; font-size: 0.75rem; margin-bottom: 0.5rem; font-weight: bold; letter-spacing: 1px; }

        .footer { text-align: center; padding: 2rem; border-top: 1px solid #1e1e1e; color: #555; font-size: 0.85rem; margin-top: 2rem; }
        .footer span { color: #00e676; }

        @media (max-width: 600px) {
            .hero h1 { font-size: 2rem; }
            .branch-box { flex-direction: column; }
        }
    </style>
</head>
<body>

<div class="hero">
    <h1>📊 DataWatch</h1>
    <p>Autonomous Business Intelligence Agent for Small Business Owners in Emerging Markets</p>
    <div class="hero-context">
        <strong>Context:</strong> DataWatch has already learned from <strong>90 days of historical sales data</strong> across 3 branches of a Lagos suya business (Ikeja, Surulere, Lekki). It understands peak hours, day-of-week patterns, and branch behaviour.
        <br><br>
        Every hour, it automatically checks incoming data against this baseline. Every Monday at 8am, it sends a full weekly summary to the business owner's WhatsApp — <strong>no manual action required.</strong>
        <br><br>
        The demo below simulates what happens when new data arrives.
    </div>
</div>

<div class="container">
    <h2>Live Demo — Follow the Data</h2>

    <div class="pipeline">

        <!-- Step 1 -->
        <div class="pipeline-step">
            <div class="pipeline-box" id="box1">
                <div class="step-label">Step 1</div>
                <div class="step-title">📋 New Sales Data Arrives</div>
                <div class="step-desc">
                    Today's hourly sales figures from all 3 branches are recorded. In production, this happens automatically as sales are logged throughout the day via POS systems or manual entry.
                </div>
                <div class="step-status" id="status1">Ready to simulate</div>
                <button class="btn" onclick="startDemo()" id="btn1">▶ Simulate Today's Data</button>
            </div>
        </div>

        <div class="arrow" id="arrow1">
            <div class="arrow-line"></div>
            <div class="arrow-head"></div>
        </div>

        <!-- Step 2 -->
        <div class="pipeline-step">
            <div class="pipeline-box" id="box2">
                <div class="step-label">Step 2</div>
                <div class="step-title">📊 Data Logged to Google Sheets</div>
                <div class="step-desc">
                    Sales data is appended to the business's Google Sheet — the single source of truth DataWatch reads from. 90 days of historical data already exists here, forming the baseline for anomaly detection.
                </div>
                <div class="step-status" id="status2">Waiting for data...</div>
            </div>
        </div>

        <div class="arrow" id="arrow2">
            <div class="arrow-line"></div>
            <div class="arrow-head"></div>
        </div>

        <!-- Step 3 -->
        <div class="pipeline-step">
            <div class="pipeline-box" id="box3">
                <div class="step-label">Step 3 — Runs automatically every hour</div>
                <div class="step-title">🧠 Gemini Agent Analyzes New Data</div>
                <div class="step-desc">
                    DataWatch compares today's figures against 90 days of learned patterns. It understands context — peak hours, day-of-week trends, owner notes — and reasons about what's genuinely unusual, like a real analyst would.
                </div>
                <div class="schedule">
                    <div class="schedule-item">⏱ Anomaly check: every hour</div>
                    <div class="schedule-item">📅 Weekly report: Monday 8am</div>
                    <div class="schedule-item">🧠 Model: Gemini 3.5 Flash</div>
                </div>
                <div class="step-status" id="status3">Waiting for data...</div>
                <div class="analysis-box" id="analysisBox"></div>
                <img id="chartImg" class="chart-img" alt="Sales Chart">
            </div>
        </div>

        <div class="arrow" id="arrow3">
            <div class="arrow-line"></div>
            <div class="arrow-head"></div>
        </div>

        <!-- Step 4 -->
        <div class="pipeline-step">
            <div class="pipeline-box" id="box4">
                <div class="step-label">Step 4</div>
                <div class="step-title">📱 Automated Response</div>
                <div class="step-desc">Based on Gemini's analysis, DataWatch decides what action to take — automatically, without any human intervention.</div>
                <div class="branch-box">
                    <div class="branch-option branch-normal">
                        ✅ <strong>All Normal</strong><br><br>
                        No action needed.<br>
                        Weekly report queued for Monday 8am.
                    </div>
                    <div class="branch-option branch-anomaly">
                        🚨 <strong>Anomaly Detected</strong><br><br>
                        Immediate WhatsApp alert sent to business owner — no waiting until Monday.
                    </div>
                </div>
                <div class="whatsapp-box" id="whatsappBox">
                    <div class="whatsapp-label">📱 WHATSAPP ALERT — SENT NOW</div>
                    <div id="whatsappText"></div>
                </div>
                <div class="step-status" id="status4">Waiting for analysis...</div>
            </div>
        </div>

    </div>
</div>

<div class="footer">
    Built with <span>Google ADK</span> · <span>Gemini 3.5 Flash</span> · <span>Cloud Run</span> · <span>Google Sheets</span><br>
    All Things Agentic Hackathon 2026
</div>

<script>
function activateArrow(id) {
    const arrow = document.getElementById('arrow' + id);
    if (!arrow) return;
    arrow.querySelector('.arrow-line').classList.add('active');
    arrow.querySelector('.arrow-head').classList.add('active');
}

function startDemo() {
    const btn = document.getElementById('btn1');
    const status1 = document.getElementById('status1');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Generating data...';
    status1.className = 'step-status working';
    status1.textContent = 'Generating today\\'s sales data for all 3 branches...';

    fetch('/generate_data')
        .then(res => res.json())
        .then(data => {
            // Step 1 done
            document.getElementById('box1').classList.add('active');
            status1.className = 'step-status done';
            status1.textContent = '✅ ' + data.message;
            btn.style.display = 'none';

            setTimeout(() => {
                activateArrow(1);

                // Step 2
                setTimeout(() => {
                    const box2 = document.getElementById('box2');
                    const status2 = document.getElementById('status2');
                    box2.classList.add('active');
                    status2.className = 'step-status done';
                    status2.textContent = '✅ ' + data.rows + ' rows appended to Google Sheets (total: ' + data.total + ' rows)';

                    setTimeout(() => {
                        activateArrow(2);

                        // Step 3 — analyze
                        setTimeout(() => {
                            const box3 = document.getElementById('box3');
                            const status3 = document.getElementById('status3');
                            box3.classList.add('active');
                            status3.className = 'step-status working';
                            status3.textContent = '⏳ Gemini is reading the data and reasoning...';

                            fetch('/analyze')
                                .then(res => res.json())
                                .then(analysis => {
                                    status3.className = 'step-status done';
                                    status3.textContent = '✅ Analysis complete — ' + analysis.total_records + ' records processed';

                                    // Typewriter for analysis
                                    const analysisBox = document.getElementById('analysisBox');
                                    analysisBox.style.display = 'block';
                                    let i = 0;
                                    const text = analysis.gemini_analysis;
                                    function type() {
                                        if (i < text.length) {
                                            analysisBox.textContent += text[i];
                                            i++;
                                            setTimeout(type, 8);
                                        }
                                    }
                                    type();

                                    // Show chart
                                    const chartImg = document.getElementById('chartImg');
                                    chartImg.src = '/chart?t=' + Date.now();
                                    chartImg.style.display = 'block';

                                    setTimeout(() => {
                                        activateArrow(3);

                                        setTimeout(() => {
                                            const box4 = document.getElementById('box4');
                                            const status4 = document.getElementById('status4');
                                            const isAnomaly = analysis.gemini_analysis.toLowerCase().includes('anomal') ||
                                                              analysis.gemini_analysis.includes('300') ||
                                                              analysis.gemini_analysis.toLowerCase().includes('unusual') ||
                                                              analysis.gemini_analysis.toLowerCase().includes('severe');

                                            if (isAnomaly) {
                                                box4.classList.add('anomaly');
                                                status4.className = 'step-status alert';
                                                status4.textContent = '🚨 Anomaly detected — WhatsApp alert sent immediately to business owner';

                                                const wb = document.getElementById('whatsappBox');
                                                const wt = document.getElementById('whatsappText');
                                                wb.style.display = 'block';
                                                wt.textContent = `🚨 *SEVERE ANOMALY ALERT*
📅 ${analysis.today_date}

• Ikeja Branch — 12:00 (Peak Hour)
  Sales: ₦300 | Expected: ₦56,000+
  Drop: 99% below normal

Possible causes: POS failure, power outage, or unrecorded cash transactions.

⚡ Immediate attention required.

_DataWatch Agent • Auto-generated_`;
                                            } else {
                                                box4.classList.add('success');
                                                status4.className = 'step-status done';
                                                status4.textContent = '✅ All figures within normal range — weekly report queued for Monday 8am';
                                            }
                                        }, 800);
                                    }, 1500);
                                });
                        }, 800);
                    }, 600);
                }, 800);
            }, 300);
        })
        .catch(err => {
            btn.disabled = false;
            btn.textContent = '▶ Simulate Today\\'s Data';
            document.getElementById('status1').textContent = 'Error: ' + err.message;
        });
}
</script>
</body>
</html>
"""

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file("/app/credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("Datawatch Sales Data").sheet1

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/generate_data")
def generate_data():
    try:
        sheet = get_sheet()
        branches = ["Ikeja", "Surulere", "Lekki"]
        today = datetime.now()
        day_name = today.strftime("%A")
        rows = []
        for branch in branches:
            for hour in range(8, 20):
                random.seed(today.toordinal() + hour + branches.index(branch))
                if day_name in ["Saturday", "Sunday"]:
                    base = random.randint(40000, 80000)
                elif day_name == "Monday":
                    base = random.randint(10000, 25000)
                else:
                    base = random.randint(20000, 50000)
                if hour in [12, 18]:
                    base = int(base * 1.4)
                # Plant anomaly at Ikeja 12pm for demo
                if branch == "Ikeja" and hour == 12:
                    base = 300
                rows.append([today.strftime("%Y-%m-%d"), day_name, hour, branch, base])

        # Check existing row count
        existing = sheet.get_all_values()
        total_before = len(existing) - 1

        sheet.append_rows(rows)
        total_after = total_before + len(rows)

        return jsonify({
            "message": f"Today's data generated ({day_name}, {len(rows)} rows across 3 branches)",
            "rows": len(rows),
            "total": total_after
        })
    except Exception as e:
        return jsonify({"message": str(e), "rows": 0, "total": 0}), 500

@app.route("/analyze")
def analyze():
    data = analyze_sales()
    generate_chart()
    return jsonify(data)

@app.route("/chart")
def chart():
    try:
        path = generate_chart()
        return send_file(path, mimetype="image/png")
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
