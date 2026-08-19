import sys
import subprocess
sys.path.insert(0, "/home/seyealadekomo/datawatch/datawatch_agent")

from agent import analyze_sales, generate_chart, generate_report

print("DataWatch Weekly Run Starting...")
analyze_sales()
generate_chart()
report = generate_report()
print(report)

# Send to WhatsApp
subprocess.run(["hermes", "send", "--to", "whatsapp:Seye", report])
print("Report sent to WhatsApp!")

# Send chart image
subprocess.run(["hermes", "send", "--to", "whatsapp:Seye", "MEDIA:/home/seyealadekomo/datawatch/sales_report.png"])
print("Chart sent to WhatsApp!")

# Save report to file
with open("/home/seyealadekomo/datawatch/latest_report.txt", "w") as f:
    f.write(report)

print("Done.")
