import hashlib, csv, qrcode, smtplib, time, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from selenium import webdriver
from selenium.webdriver.common.by import By

# === CONFIG ===
NUM_USERS = 10000
CSV_FILE = "mega_log.csv"
EMAIL_TO = "you@yourdomain.com"  # CHANGE
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"  # CHANGE
SMTP_PASS = "your_app_password"     # CHANGE (App Password!)

# === Setup ===
d = webdriver.Chrome(options=webdriver.ChromeOptions().add_argument('--headless=new'))
d.get("http://127.0.0.1:5000")
os.makedirs("qrcodes", exist_ok=True)

with open(CSV_FILE, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["Email","Code","Status","Time","QR_Path"])
    for i in range(NUM_USERS):
        email = f"user{i}@game.com"
        code = '-'.join(hashlib.sha256(email.encode()).hexdigest()[:16][j:j+4] for j in range(0,16,4)).translate(str.maketrans('0123456789abcdef','abcdefghijklmnop'))
        
        d.find_element(By.NAME,"code").clear(); d.find_element(By.NAME,"code").send_keys(code); d.find_element(By.TAG_NAME,"button").click()
        status = "Activated" if "Welcome" in d.page_source else "Failed"
        
        qr = qrcode.make(code); qr_path = f"qrcodes/{code}.png"; qr.save(qr_path)
        w.writerow([email, code, status, time.strftime("%H:%M:%S"), qr_path])
        
        d.get("http://127.0.0.1:5000")  # reset
        if i % 100 == 0: print(f"{i} done...")

d.quit(); print("Activation complete!")

# === Email CSV + Sample QRs ===
msg = MIMEMultipart()
msg['From'] = SMTP_USER; msg['To'] = EMAIL_TO; msg['Subject'] = f"10K Game Activations Complete"

body = f"Attached: {NUM_USERS} codes + QRs"
msg.attach(MIMEText(body, 'plain'))

# Attach CSV
with open(CSV_FILE, "rb") as a:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(a.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {CSV_FILE}")
    msg.attach(part)

# Attach 5 sample QRs
for sample in [f"qrcodes/{hashlib.sha256(f'user{i}@game.com'.encode()).hexdigest()[:16].translate(str.maketrans('0123456789abcdef','abcdefghijklmnop'))}.png" for i in range(5)]:
    if os.path.exists(sample):
        with open(sample, "rb") as a:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(a.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(sample)}")
            msg.attach(p)

# Send
s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
s.starttls(); s.login(SMTP_USER, SMTP_PASS)
s.send_message(msg); s.quit()
print("CSV + QRs emailed!")