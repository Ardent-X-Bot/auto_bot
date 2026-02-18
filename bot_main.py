# bot_main.py
import os
import requests
import subprocess
import time

from menu_config import BOT_TOKEN, CHAT_ID, COMMAND_MAPPING, SHORTCUTS_MAPPING, send_menu

# ------------------------------
DEFAULT_DIR = os.path.expanduser("~/")
current_dir = DEFAULT_DIR

LOG_FILE = os.path.expanduser("~/tg/logs/bot_output.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ------------------------------
def log_output(output):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(output + "\n")

# ------------------------------
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except requests.exceptions.RequestException:
        return {}

# ------------------------------
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except requests.exceptions.RequestException:
        print("⚠️ Telegram offline or cannot send message")

# ------------------------------
def change_cwd(msg):
    global current_dir
    if msg.strip() == "/cwd HOME":
        current_dir = DEFAULT_DIR
        os.chdir(current_dir)
        return f"✅ Directory changed to home: {current_dir}"
    elif msg.startswith("/cwd "):
        new_dir = msg[5:].strip()
        new_dir = os.path.expanduser(new_dir)
        try:
            os.chdir(new_dir)
            current_dir = new_dir
            return f"✅ Directory changed to: {current_dir}"
        except FileNotFoundError:
            return f"❌ Directory not found: {new_dir}"
        except Exception as e:
            return f"❌ Error changing directory: {e}"
    return None

# ------------------------------
def parse_command(msg):
    if msg.startswith("/cwd"):
        return "CWD_COMMAND"
    elif msg.startswith("/run "):
        return {"cmd": msg[5:]}  # only run once
    elif msg in COMMAND_MAPPING:
        return COMMAND_MAPPING[msg]
    elif msg in SHORTCUTS_MAPPING:
        return SHORTCUTS_MAPPING[msg]
    return None

# ------------------------------
def execute_command(entry):
    global current_dir
    try:
        # Determine command
        if isinstance(entry, str):
            cmd = entry
        elif isinstance(entry, dict):
            cmd = entry.get("cmd")
        else:
            return "❌ Invalid command entry"

        # Always respect user cwd
        cwd = current_dir

        # Run command
        if isinstance(cmd, list):
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)

        output = result.stdout + (("\n" + result.stderr) if result.stderr else "")
        output = output.strip()
        log_output(output)

        # Send confirmation if mapping has confirm message
        if isinstance(entry, dict) and "confirm" in entry:
            return entry["confirm"]

        return output if output else "✅ Command executed (no output)"
    except Exception as e:
        return f"❌ Error executing command:\n{e}"

# ------------------------------
def main():
    last_update_id = None
    print("Bot running...")

    # Bot started message
    send_message("🚀 Bot started and ready!")

    # Send menu on start
    send_menu(BOT_TOKEN, CHAT_ID)

    while True:
        updates = get_updates(last_update_id)
        if not updates:
            time.sleep(3)
            continue

        for update in updates.get("result", []):
            last_update_id = update["update_id"] + 1
            msg = update.get("message", {}).get("text")
            chat_id = update.get("message", {}).get("id")

            if not msg or str(chat_id) != str(CHAT_ID):
                continue

            # Handle /cwd
            if msg.startswith("/cwd"):
                resp = change_cwd(msg)
                send_message(resp)
                continue  # prevent double execution

            # Determine command
            entry = parse_command(msg)
            if not entry:
                send_message("⚠️ Unknown command. Use menu buttons or /run <command>")
                continue

            # Execute only once
            output = execute_command(entry)
            send_message(output)

        time.sleep(1)

# ------------------------------
if __name__ == "__main__":
    main()
