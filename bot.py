import telebot
from telebot.types import Message

# Enter your bot token here
BOT_TOKEN = "your_token_here"

bot = telebot.TeleBot(BOT_TOKEN)

# Stores users waiting for a partner
waiting_users = []

# Stores active chat pairs
active_chats = {}  # {user1: user2, user2: user1}

def pair_users():
    """Pair users if two are available."""
    if len(waiting_users) >= 2:
        u1 = waiting_users.pop(0)
        u2 = waiting_users.pop(0)
        active_chats[u1] = u2
        active_chats[u2] = u1

        bot.send_message(u1, "🎉 You are now connected! Say hi 👋\nType /next to skip.")
        bot.send_message(u2, "🎉 You are now connected! Say hi 👋\nType /next to skip.")

# ---------------- COMMAND HANDLERS ---------------- #

@bot.message_handler(commands=['start'])
def start(message: Message):
    user = message.chat.id

    if user in active_chats:
        bot.send_message(user, "⚠ You are already chatting.\nType /next to skip.")
        return

    if user not in waiting_users:
        waiting_users.append(user)
        bot.send_message(user, "⏳ Searching for a partner...")
        pair_users()

@bot.message_handler(commands=['next'])
def next_cmd(message: Message):
    user = message.chat.id

    if user not in active_chats:
        bot.send_message(user, "❗ You are not chatting.\nType /start to find a partner.")
        return

    partner = active_chats[user]

    # Disconnect both
    del active_chats[user]
    del active_chats[partner]

    bot.send_message(partner, "⚠ Your partner left! Type /start to find a new one.")
    bot.send_message(user, "🔎 Searching for a new partner...")

    waiting_users.append(user)
    pair_users()

@bot.message_handler(commands=['stop'])
def stop_cmd(message: Message):
    user = message.chat.id

    if user in waiting_users:
        waiting_users.remove(user)

    if user in active_chats:
        partner = active_chats[user]
        del active_chats[user]
        del active_chats[partner]
        bot.send_message(partner, "⚠ Partner left the chat.")
    
    bot.send_message(user, "❌ You stopped the chat.\nType /start to find a new partner.")

# ---------------- MESSAGE RELAY ---------------- #

@bot.message_handler(func=lambda msg: True)
def relay(message: Message):
    user = message.chat.id

    if user not in active_chats:
        bot.send_message(user, "👆 You're not connected.\nUse /start to find a partner.")
        return
    
    partner = active_chats[user]
    bot.send_message(partner, message.text)


# ---------------- START BOT ---------------- #
bot.polling(none_stop=True)

