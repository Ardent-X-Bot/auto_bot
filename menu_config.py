# menu_config.py
import os
import json
import requests

# ------------------------------
BOT_TOKEN = "8236424828:AAFizE7LXRGv0W9DWqYxV5vat8o19VATjfQ"
CHAT_ID = "7008420572"

# ------------------------------
MENU_BUTTONS = [
    ["pkg update -y", "pwd", "Storage"],
    ["backup", "start_script", "screen info"]
]

# ------------------------------
# Command Mapping: button → command + optional cwd
COMMAND_MAPPING = {
    "pkg update -y": {"cmd": "pkg update -y"},
    "pwd": {"cmd": "pwd"},
    "Storage": {"cmd": "ls", "cwd": "~/storage/shared"},
    "backup": {"cmd": ["git", "clone", "https://github.com/Cod3r-Ak/TermuX-Custom.git"], "cwd": "~/tg", "confirm": "✅ Backup/clone completed!"},
    "start_script": {"cmd": ["python3", "test.py"], "cwd": "~/python"},
    "screen info": {"cmd": "cat ~/tg/logs/bot_output.log"}
}

# ------------------------------
# Shortcut commands: /update, /pwd etc
SHORTCUTS_MAPPING = {
    "/update": COMMAND_MAPPING["pkg update -y"],
    "/pwd": COMMAND_MAPPING["pwd"],
    "/storage": COMMAND_MAPPING["Storage"],
    "/backup": COMMAND_MAPPING["backup"],
    "/script": COMMAND_MAPPING["start_script"],
    "/screen": COMMAND_MAPPING["screen info"]
}

# ------------------------------
def send_menu(bot_token: str, chat_id: str):
    keyboard = {
        "keyboard": MENU_BUTTONS,
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "📟 Select a command from the menu or use /run <command>:",
        "reply_markup": json.dumps(keyboard)
    }
    try:
        requests.post(url, data=payload)
    except:
        print("⚠️ Could not send menu")
