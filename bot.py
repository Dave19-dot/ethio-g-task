import telebot
from telebot import types
import random
import string
import threading

USER_BOT_TOKEN = "9145697620:AAFH7S9qA6THJOCB7XS7e_mSKvpN9oX2YtY"
ADMIN_BOT_TOKEN = "8928751621:AAFYkO8mzPDhOiA2w3HCz247_9b1rvo-b84"
REQUIRED_CHANNEL = "@EthioGtask"
ADMIN_ID = 123456789

user_bot = telebot.TeleBot(USER_BOT_TOKEN)
admin_bot = telebot.TeleBot(ADMIN_BOT_TOKEN)

users_db = {}
emails_db = []
withdrawals_db = []

def generate_fake_email():
    first_names = ["abebe", "kebede", "dawit", "meron", "hana", "tadesse", "chala"]
    last_names = ["bekele", "alemu", "tadesse", "mulugeta", "kebede", "girma"]
    f_name = random.choice(first_names)
    l_name = random.choice(last_names)
    number = random.randint(100, 9999)
    email = f"{f_name}.{l_name}{number}@gmail.com"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    recovery = f"rec_{f_name}{number}@gmail.com"
    return f_name.capitalize(), l_name.capitalize(), email, password, recovery

def check_membership(user_id):
    try:
        member = user_bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        if member.status in ['member', 'creator', 'administrator']:
            return True
    except:
        pass
    return False

def show_main_menu(user_id):
    lang = users_db[user_id]['lang']
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if lang == 'am':
        b1, b2, b3, b4, b5, b6 = "📩 ኢሜይል ክፈት", "💰 Balance & Withdraw", "👥 ጓደኛ ጋብዝ", "⚙️ Setting", "🆘 Help", "🌐 Language"
    else:
        b1, b2, b3, b4, b5, b6 = "📩 Open Email", "💰 Balance & Withdraw", "👥 Invite Friends", "⚙️ Setting", "🆘 Help", "🌐 Language"
    markup.add(types.KeyboardButton(b1), types.KeyboardButton(b2))
    markup.add(types.KeyboardButton(b3), types.KeyboardButton(b4))
    markup.add(types.KeyboardButton(b5), types.KeyboardButton(b6))
    welcome_msg = (
        "✨ **እንኳን ወደ Ethio G Task በደህና መጡ!** 🚀\n\n"
        "እዚህ ቦት ላይ ኢሜይሎችን በመክፈት እና ጓደኞችን በመጋበዝ ገንዘብ ማግኘት ይችላሉ። 💵\n"
        "ከታች ካሉት አማራጮች አንዱን ይምረጡ 👇"
    ) if lang == 'am' else (
        "✨ **Welcome to Ethio G Task!** 🚀\n\n"
        "You can earn money by opening emails and inviting friends here. 💵\n"
        "Choose an option from below 👇"
    )
    user_bot.send_message(user_id, welcome_msg, reply_markup=markup, parse_mode="Markdown")

@user_bot.message_handler(commands=['start'])
def user_start(message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) > 1 and user_id not in users_db:
        try:
            ref_id = int(args[1])
            if ref_id != user_id and ref_id in users_db:
                users_db[ref_id]['balance'] += 5
                users_db[ref_id]['ref_count'] = users_db[ref_id].get('ref_count', 0) + 1
                user_bot.send_message(ref_id, f"🎉 እንኳን ደስ አለዎት! 1 ሰው በመጋበዝዎ 5 ብር አግኝተዋል! 💰")
        except:
            pass
    if user_id not in users_db:
        users_db[user_id] = {'lang': 'am', 'balance': 0.0, 'ref_count': 0, 'phone': ''}
    if not check_membership(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 ቻናሉን Join አድርግ", url=f"https://t.me/{REQUIRED_CHANNEL.replace('@','')}"))
        markup.add(types.InlineKeyboardButton("✅ ቼክ አድርግ / Check", callback_data="check_join"))
        user_bot.send_message(user_id, f"👋 ሰላም! ወደ **Ethio G Task** በደህና መጡ! 🌟\n\nቦቱን ለመጠቀም አስቀድመው ቻናላችንን Join መደረግ አለብዎት 👇", reply_markup=markup, parse_mode="Markdown")
        return
    show_main_menu(user_id)

@user_bot.callback_query_handler(func=lambda call: call.data == "check_join")
def callback_check_join(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        user_bot.answer_callback_query(call.id, "✅ በስኬት ቻናሉን ተቀላቅለዋል!")
        user_bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(user_id)
    else:
        user_bot.answer_callback_query(call.id, "❌ እባክዎ መጀመሪያ ቻናሉን Join ይበሉ!", show_alert=True)
@user_bot.message_handler(func=lambda message: True)
def handle_user_messages(message):
    user_id = message.from_user.id
    text = message.text
    if user_id not in users_db:
        users_db[user_id] = {'lang': 'am', 'balance': 0.0, 'ref_count': 0, 'phone': ''}
    if text in ["🌐 Language", "🌐 ቋንቋ"]:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_am"), types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
        user_bot.send_message(user_id, "ቋንቋ ይምረጡ / Choose Language:", reply_markup=markup)
        return
    if text in ["📩 ኢሜይል ክፈት", "📩 Open Email"]:
        f_name, l_name, email, password, recovery = generate_fake_email()
        response_text = f"✅ **ኢሜይል በተሳካ ሁኔታ ተፈጠረ!** 🟢\n\n👤 **First Name:** `{f_name}`\n👤 **Last Name:** `{l_name}`\n📧 **Email:** `{email}`\n🔑 **Password:** `{password}`\n🔄 **Recovery Email:** `{recovery}`\n\n🎁 **ለዚህ ኢሜይል 10 ብር ወደ አካውንትዎ ገብቷል!** 💵"
        users_db[user_id]['balance'] += 10.0
        emails_db.append({'user_id': user_id, 'name': message.from_user.first_name, 'email': email, 'status': 'Verified ✅'})
        user_bot.send_message(user_id, response_text, parse_mode="Markdown")
        return
    if text in ["💰 Balance & Withdraw", "💰 Balance"]:
        balance = users_db[user_id]['balance']
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💸 Withdraw (ቴሌብር)", callback_data="withdraw_start"))
        msg = f"💳 **ቀሪ ሂሳብዎ:** **{balance} ብር**\n👥 የጋበዟቸው: {users_db[user_id].get('ref_count', 0)} ሰው\n\n⚠️ *ብር ለማውጣት ቢያንስ 50 ብር ሊኖርዎት ይገባል!*"
        user_bot.send_message(user_id, msg, reply_markup=markup, parse_mode="Markdown")
        return
    if text in ["👥 ጓደኛ ጋብዝ", "👥 Invite Friends"]:
        bot_info = user_bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        msg = f"🔗 **የእርስዎ መጋበዣ ሊንክ:**\n\n`{ref_link}`\n\n🎁 1 ሰው ሲጋብዙ 5 ብር ያገኛሉ!"
        user_bot.send_message(user_id, msg, parse_mode="Markdown")
        return

@user_bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def callback_language(call):
    user_id = call.from_user.id
    lang = call.data.split("_")[1]
    users_db[user_id]['lang'] = lang
    user_bot.answer_callback_query(call.id, "✅ Language updated!")
    show_main_menu(user_id)

@user_bot.callback_query_handler(func=lambda call: call.data == "withdraw_start")
def callback_withdraw(call):
    user_id = call.from_user.id
    if users_db[user_id]['balance'] < 50:
        user_bot.answer_callback_query(call.id, "❌ ብር ለማውጣት ቢያንስ 50 ብር መድረስ አለብዎት!", show_alert=True)
        return
    msg = user_bot.send_message(user_id, "📱 የቴሌብር (Telebirr) ስልክ ቁጥርዎን ይላኩ (ምሳሌ: 0912345678):")
    user_bot.register_next_step_handler(msg, process_withdrawal_phone)

def process_withdrawal_phone(message):
    user_id = message.from_user.id
    phone = message.text
    balance = users_db[user_id]['balance']
    withdrawals_db.append({'user_id': user_id, 'name': message.from_user.first_name, 'amount': balance, 'phone': phone, 'status': 'Pending ⏳'})
    admin_bot.send_message(ADMIN_ID, f"🚨 **አዲስ የብር ማውጣት ጥያቄ!** 💸\n\n👤 ስም: {message.from_user.first_name}\n💵 መጠን: **{balance} ብር**\n📱 ቴሌብር: `{phone}`", parse_mode="Markdown")
    users_db[user_id]['balance'] = 0.0
    user_bot.send_message(user_id, "✅ ጥያቄዎ ተቀብሏል! በቅርቡ ይላክልዎታል። ⏳")

@admin_bot.message_handler(commands=['start'])
def admin_start(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton("📊 Task / መረጃ"), types.KeyboardButton("🏆 ብዙ የሰራ ሰው"))
    admin_bot.send_message(message.chat.id, "🛠️ **አስተዳዳሪ ፓነል (Admin Panel)**", reply_markup=markup, parse_mode="Markdown")

@admin_bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
def handle_admin_messages(message):
    text = message.text
    if text == "📊 Task / መረጃ":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📋 የተሰሩ ኢሜይሎች", callback_data="admin_emails"))
        markup.add(types.InlineKeyboardButton("💸 የብር ማውጣት ጥያቄዎች", callback_data="admin_withdrawals"))
        admin_bot.send_message(message.chat.id, "📊 **መረጃዎችን ለመመልከት ይምረጡ:**", reply_markup=markup)

@admin_bot.callback_query_handler(func=lambda call: call.data == "admin_emails")
def callback_admin_emails(call):
    if not emails_db:
        admin_bot.answer_callback_query(call.id, "📭 የተፈጠረ ኢሜይል የለም።", show_alert=True)
        return
    msg = "📋 **የተሰሩ ኢሜይሎች:**\n\n"
    for item in emails_db[-10:]:
        msg += f"- {item['name']}: `{item['email']}`\n"
    admin_bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

@admin_bot.callback_query_handler(func=lambda call: call.data == "admin_withdrawals")
def callback_admin_withdrawals(call):
    pending_wd = [w for w in withdrawals_db if w['status'] == 'Pending ⏳']
    if not pending_wd:
        admin_bot.answer_callback_query(call.id, "📭 የሚጠብቅ የክፍያ ጥያቄ የለም።", show_alert=True)
        return
    for idx, w in enumerate(pending_wd):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ ሂሳቡ ተልኳል (Approve)", callback_data=f"approve_wd_{w['user_id']}"))
        msg = f"💸 **ጥያቄ #{idx+1}**\n👤 ስም: {w['name']}\n💵 መጠን: **{w['amount']} ብር**\n📱 ቴሌብር: `{w['phone']}`"
        admin_bot.send_message(call.message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@admin_bot.callback_query_handler(func=lambda call: call.data.startswith("approve_wd_"))
def callback_approve_withdrawal(call):
    target_user_id = int(call.data.split("_")[2])
    for w in withdrawals_db:
        if w['user_id'] == target_user_id and w['status'] == 'Pending ⏳':
            w['status'] = 'Completed ✅'
    try:
        user_bot.send_message(target_user_id, "✅ **የጠየቁት ገንዘብ ወደ ቴሌብር አካውንትዎ ተልኳል!** 💸")
    except:
        pass
    admin_bot.answer_callback_query(call.id, "✅ ተጠናቋል!")

if __name__ == "__main__":
    t1 = threading.Thread(target=user_bot.infinity_polling, kwargs={'skip_pending': True})
    t2 = threading.Thread(target=admin_bot.infinity_polling, kwargs={'skip_pending': True})
    t1.start()
    t2.start()
    t1.join()
    t2.join()
