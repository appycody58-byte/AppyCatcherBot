import os
import subprocess
import time
from datetime import datetime
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# ===================== CONFIG =====================
BOT_TOKEN = "8223051433:AAGFGLFBb6Ke6Qqk6EJiwXFAaluvIWdLjIY"
GITHUB_REPO = None  # Set your repo if you want auto-update: "https://github.com/username/repo.git"
BOT_FOLDER = "mybot"
UPDATE_INTERVAL = 3600  # seconds, 1 hour
OWNER_CHAT_ID = None  # Set your Telegram ID to receive crash/restart alerts
# ===================================================

# Install required library
subprocess.run(["pip", "install", "--upgrade", "python-telegram-bot"], check=True)

# Logging function
def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {msg}")
    with open("logs.txt", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

# Send Telegram alert to owner
def alert_owner(message):
    if OWNER_CHAT_ID:
        try:
            bot = Bot(token=BOT_TOKEN)
            bot.send_message(chat_id=OWNER_CHAT_ID, text=message)
        except Exception as e:
            log(f"Failed to send alert: {e}")

# Clone or update GitHub repo if configured
def git_update():
    if GITHUB_REPO:
        if not os.path.exists(BOT_FOLDER):
            log("Cloning bot repo from GitHub...")
            subprocess.run(["git", "clone", GITHUB_REPO, BOT_FOLDER], check=True)
        else:
            log("Pulling latest updates from GitHub...")
            os.chdir(BOT_FOLDER)
            subprocess.run(["git", "fetch", "origin"], check=True)
            branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
            subprocess.run(["git", "reset", "--hard", f"origin/{branch}"], check=True)
            os.chdir("..")

# Run the bot
def run_bot():
    log("Starting bot...")
    bot = Bot
