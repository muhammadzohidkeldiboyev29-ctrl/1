from datetime import datetime
import random
import sqlite3
from threading import Thread
from flask import Flask
import telebot
from telebot import types

TOKEN = "8816940858:AAF2AdMub0XRMqBOYeyyPyjNbwZDShjEy9o"
ADMIN_ID = 8753350906

bot = telebot.TeleBot(TOKEN)
user_states = {}
DB_NAME = "bot_database.db"

# --- RENDER 24/7 UCHUN FLASK SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# -------------------------------------

# Har bir til uchun barcha matnlar va tugmalar
LANG_TEXTS = {
    "uz": {
        "menu": "✅ Asosiy menyu:",
        "search_btn": "🔍 Qidirish",
        "random_btn": "🎲 Tasodifiy",
        "vip_btn": "💎 Premium Obuna",
        "lang_btn": "🌐 Tilni o'zgartirish",
        "ad_btn": "📢 Reklama",
        "settings_btn": "⚙️ Admin sozlamalari",
        "search_prompt": "🔎 Kino kodini yuboring (masalan: `1`):",
        "movie_not_found": "❌ `{code}` kodi topilmadi.",
        "movies_not_found": "❌ Kinolar topilmadi.",
        "vip_choose_period": "💎 **VIP Premium Obuna**\n\nMuddatni tanlang:",
        "card_info": "💳 **Karta raqami:** `6262 5701 4806 4381`\n👤 **Ism Familiya:** Obidjonova M.\n\n📥 To'lov qilib, chek rasmini shu botga yuboring!",
        "sub_required": "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
        "sub_btn": "✅ Obunani tekshirish",
        "vip_only": "💎 Bu kino faqat VIP obunachilar uchun!",
        "lang_changed": "🇺🇿 Til O'zbek tiliga o'zgartirildi ✅"
    },
    "ru": {
        "menu": "✅ Главное меню:",
        "search_btn": "🔍 Поиск",
        "random_btn": "🎲 Случайный",
        "vip_btn": "💎 VIP Подписка",
        "lang_btn": "🌐 Сменить язык",
        "ad_btn": "📢 Реклама",
        "settings_btn": "⚙️ Настройки админа",
        "search_prompt": "🔎 Отправьте код фильма (например: `1`):",
        "movie_not_found": "❌ Код `{code}` не найден.",
        "movies_not_found": "❌ Фильмы не найдены.",
        "vip_choose_period": "💎 **VIP Премиум Подписка**\n\nВыберите срок:",
        "card_info": "💳 **Номер карты:** `6262 5701 4806 4381`\n👤 **ФИО:** Obidjonova M.\n\n📥 Сделайте перевод и отправьте скриншот чека сюда!",
        "sub_required": "⚠️ Для использования бота подпишитесь на каналы:",
        "sub_btn": "✅ Проверить подписку",
        "vip_only": "💎 Этот фильм доступен только для VIP подписчиков!",
        "lang_changed": "🇷🇺 Язык изменен на Русский ✅"
    },
    "en": {
        "menu": "✅ Main menu:",
        "search_btn": "🔍 Search",
        "random_btn": "🎲 Random",
        "vip_btn": "💎 VIP Subscription",
        "lang_btn": "🌐 Language",
        "ad_btn": "📢 Ads",
        "settings_btn": "⚙️ Admin Settings",
        "search_prompt": "🔎 Send movie code (e.g., `1`):",
        "movie_not_found": "❌ Code `{code}` not found.",
        "movies_not_found": "❌ No movies found.",
        "vip_choose_period": "💎 **VIP Premium Subscription**\n\nSelect period:",
        "card_info": "💳 **Card Number:** `6262 5701 4806 4381`\n👤 **Name:** Obidjonova M.\n\n📥 Make the payment and send the receipt screenshot here!",
        "sub_required": "⚠️ Please subscribe to channels to use the bot:",
        "sub_btn": "✅ Check Subscription",
        "vip_only": "💎 This movie is for VIP subscribers only!",
        "lang_changed": "🇬🇧 Language changed to English ✅"
    }
}

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, lang TEXT DEFAULT 'uz', joined_date TEXT, is_vip INTEGER DEFAULT 0, status TEXT DEFAULT 'active')")
    cursor.execute("CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, video_id TEXT, is_vip INTEGER DEFAULT 0, downloads INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY AUTOINCREMENT, channel_username TEXT)")
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def get_user_lang(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "uz"

def set_user_lang(user_id, lang):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

def check_channels_subscription(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_username FROM channels")
    channels = cursor.fetchall()
    conn.close()

    if not channels:
        return True

    for (ch,) in channels:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception:
            pass
    return True

def show_subscription_alert(chat_id, lang):
    t = LANG_TEXTS[lang]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT channel_username FROM channels")
    channels = cursor.fetchall()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    for (ch,) in channels:
        markup.row(types.InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.replace('@', '')}"))
    markup.row(types.InlineKeyboardButton(t["sub_btn"], callback_data="check_sub"))
    bot.send_message(chat_id, t["sub_required"], reply_markup=markup)

def show_main_menu(chat_id, user_id):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(t["search_btn"], t["random_btn"])
    markup.row(t["vip_btn"], t["lang_btn"])
    markup.row(t["ad_btn"])
    if user_id == ADMIN_ID:
        markup.row(t["settings_btn"])
    bot.send_message(chat_id, t["menu"], reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone()
    if not exists:
        cursor.execute("INSERT INTO users (user_id, username, joined_date, status) VALUES (?, ?, ?, 'active')", 
                       (user_id, message.from_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    else:
        cursor.execute("UPDATE users SET status = 'active' WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    if message.text and message.text.startswith('/start kino_'):
        code = message.text.split('_')[1]
        process_user_movie_request(message.chat.id, user_id, code)
        return

    show_main_menu(message.chat.id, user_id)

@bot.message_handler(func=lambda m: m.text in ["🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Language"])
def change_lang_btn(m):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(m.chat.id, "🌍 Tilni tanlang / Выберите язык / Select language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def callback_language(call):
    lang = call.data.split('_')[1]
    user_id = call.from_user.id
    set_user_lang(user_id, lang)
    t = LANG_TEXTS[lang]
    
    bot.answer_callback_query(call.id, t["lang_changed"])
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    show_main_menu(call.message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def check_subscription_callback(call):
    user_id = call.from_user.id
    lang = get_user_lang(user_id)
    if check_channels_subscription(user_id):
        bot.answer_callback_query(call.id, "Rahmat! Obuna tasdiqlandi ✅")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        bot.send_message(call.message.chat.id, "✅ Obunangiz tekshirildi! Endi kino kodini yuboring.")
    else:
        bot.answer_callback_query(call.id, "Siz hali hamma kanallarga obuna bo'lmadingiz ❌", show_alert=True)

@bot.message_handler(func=lambda m: m.text in ["💎 Premium Obuna", "💎 VIP Подписка", "💎 VIP Subscription"])
def vip_menu(m):
    lang = get_user_lang(m.from_user.id)
    t = LANG_TEXTS[lang]
    markup = types.InlineKeyboardMarkup()
    if lang == 'uz':
        markup.row(types.InlineKeyboardButton("1 oy — 13,000 so'м", callback_data="vip_uz_1"))
        markup.row(types.InlineKeyboardButton("3 oy — 20,000 so'м", callback_data="vip_uz_3"))
        markup.row(types.InlineKeyboardButton("6 oy — 32,000 so'м", callback_data="vip_uz_6"))
    elif lang == 'ru':
        markup.row(types.InlineKeyboardButton("1 месяц — 300 руб", callback_data="vip_ru_1"))
        markup.row(types.InlineKeyboardButton("3 месяца — 420 руб", callback_data="vip_ru_3"))
        markup.row(types.InlineKeyboardButton("6 месяцев — 550 руб", callback_data="vip_ru_6"))
    else:
        markup.row(types.InlineKeyboardButton("1 month — $12", callback_data="vip_en_1"))
        markup.row(types.InlineKeyboardButton("3 months — $15", callback_data="vip_en_3"))
        markup.row(types.InlineKeyboardButton("6 months — $22", callback_data="vip_en_6"))
    bot.send_message(m.chat.id, t["vip_choose_period"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('vip_'))
def callback_vip_period(call):
    parts = call.data.split('_')
    lang = parts[1]
    period = parts[2]
    t = LANG_TEXTS[lang]
    text = f"💎 **VIP Obuna ({period} oy)**\n\n" + t["card_info"]
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(content_types=['photo'], func=lambda m: m.from_user.id != ADMIN_ID)
def handle_payment_screenshot(message):
    user_id = message.from_user.id
    photo_id = message.photo[-1].file_id
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"accept_vip_{user_id}"),
        types.InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_vip_{user_id}")
    )
    bot.send_photo(ADMIN_ID, photo_id, caption=f"💳 **Yangi to'lov cheki!**\nFoydalanuvchi ID: `{user_id}`", parse_mode="Markdown", reply_markup=markup)
    bot.reply_to(message, "✅ Chekingiz admingacha yetib bordi! Tez orada tekshiriladi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_vip_') or call.data.startswith('reject_vip_'))
def admin_vip_decision(call):
    if call.from_user.id != ADMIN_ID:
        return
    data = call.data.split('_')
    action = data[0]
    user_id = int(data[2])
    
    if action == 'accept':
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "Tasdiqlandi ✅")
        bot.send_message(user_id, "🎉 Tabriklaymiz! VIP obunangiz faollashdi! ✅")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n✅ QABUL QILINGAN")
    else:
        bot.answer_callback_query(call.id, "Rad etildi ❌")
        bot.send_message(user_id, "❌ To'lov chekingiz rad etildi.")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ RAD ETILGAN")

@bot.message_handler(func=lambda m: m.text in ["📢 Reklama", "📢 Реклама", "📢 Ads"])
def ad_info(m):
    bot.send_message(m.chat.id, "📢 **Reklama va kanal rivojlantirish uchun:**\n\nMurojaat uchun: @mhdnvwv", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text in ["⚙️ Admin sozlamalari", "⚙️ Настройки админа", "⚙️ Admin Settings"])
def admin_settings_menu(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Statistika", "🎬 Kino qo'shish")
    markup.row("💎 VIP kino qo'shish", "➕ Obuna qo'shish")
    markup.row("🗑 Obunani o'chirish", "⬅️ Asosiy menyu")
    bot.send_message(m.chat.id, "⚙️ Admin panel:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⬅️ Asosiy menyu")
def back_to_main(m):
    show_main_menu(m.chat.id, m.from_user.id)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 Statistika")
def admin_stats(m):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM movies")
    movies_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
    vip_count = c.fetchone()[0]
    conn.close()
    
    text = f"📊 **Statistika:**\n\n👥 Jami foydalanuvchilar: {total_users}\n💎 VIP obunachilar: {vip_count}\n🎬 Kinolar soni: {movies_count}"
    bot.reply_to(m, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "➕ Obuna qo'shish")
def add_channel_start(m):
    user_states[m.from_user.id] = {'state': 'waiting_for_channel'}
    bot.reply_to(m, "📢 Majburiy kanal username'ini yuboring (masalan: `@kanal_nomi`):")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_channel')
def save_channel(m):
    channel = m.text.strip()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO channels (channel_username) VALUES (?)", (channel,))
    conn.commit()
    conn.close()
    bot.reply_to(m, f"✅ `{channel}` kanallar ro'yxatiga qo'shildi!", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "🗑 Obunani o'chirish")
def delete_channel_list(m):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, channel_username FROM channels")
    channels = c.fetchall()
    conn.close()
    
    if not channels:
        bot.reply_to(m, "❌ Majburiy kanallar mavjud emas.")
        return
        
    markup = types.InlineKeyboardMarkup()
    for ch_id, ch_name in channels:
        markup.row(types.InlineKeyboardButton(f"❌ O'chirish: {ch_name}", callback_data=f"del_ch_{ch_id}"))
    bot.reply_to(m, "🗑 O'chirmoqchi bo'lgan kanalni tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('del_ch_'))
def remove_channel_callback(call):
    if call.from_user.id != ADMIN_ID:
        return
    ch_id = int(call.data.split('_')[2])
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM channels WHERE id = ?", (ch_id,))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "O'chirildi ✅")
    bot.edit_message_text("🗑 Kanal majburiy ro'yxatdan o'chirildi!", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text in ["🎬 Kino qo'shish", "💎 VIP kino qo'shish"])
def admin_add_movie(m):
    is_vip = 1 if "VIP" in m.text else 0
    user_states[m.from_user.id] = {'state': 'waiting_for_movie_video', 'is_vip': is_vip}
    bot.reply_to(m, "🎬 Kino videosini yuboring:")

@bot.message_handler(content_types=['video'], func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_movie_video')
def get_movie_video(m):
    user_states[m.from_user.id]['video_id'] = m.video.file_id
    user_states[m.from_user.id]['state'] = 'waiting_for_movie_code'
    bot.reply_to(m, "✅ Video qabul qilindi. Endi kino kodini yuboring (masalan: `1`):")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_movie_code')
def get_movie_code(m):
    code = m.text.strip()
    data = user_states.get(m.from_user.id, {})
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO movies (code, video_id, is_vip, downloads) VALUES (?, ?, ?, 0)", 
              (code, data.get('video_id'), data.get('is_vip', 0)))
    conn.commit()
    conn.close()
    bot.reply_to(m, f"🎉 Kino saqlandi! Kodi: `{code}`", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(func=lambda m: m.text in ["🎲 Tasodifiy", "🎲 Случайный", "🎲 Random"])
def random_m(message):
    process_user_random_request(message.chat.id, message.from_user.id)

def process_user_random_request(chat_id, user_id):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    if user_id != ADMIN_ID and not check_channels_subscription(user_id):
        show_subscription_alert(chat_id, lang)
        return

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT code, video_id, is_vip FROM movies")
    movies = cursor.fetchall()
    conn.close()
    
    if not movies:
        bot.send_message(chat_id, t["movies_not_found"])
        return
        
    code, video_id, is_vip = random.choice(movies)
    
    if is_vip:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        is_user_vip = user_row[0] if user_row else 0
        if not is_user_vip and user_id != ADMIN_ID:
            bot.send_message(chat_id, t["vip_only"])
            return

    bot.send_video(chat_id, video_id, caption=f"🎬 Kino kodi: `{code}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🔍 Qidirish", "🔍 Поиск", "🔍 Search"])
def search_movie_prompt(m):
    user_id = m.from_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]

    if user_id != ADMIN_ID and not check_channels_subscription(user_id):
        show_subscription_alert(m.chat.id, lang)
        return

    user_states[user_id] = {'state': 'waiting_for_search_code'}
    bot.send_message(m.chat.id, t["search_prompt"], parse_mode="Markdown")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_search_code')
def process_movie_search(m):
    code = m.text.strip()
    user_id = m.from_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT video_id, is_vip FROM movies WHERE code = ?", (code,))
    movie = cursor.fetchone()
    conn.close()
    
    if not movie:
        bot.send_message(m.chat.id, t["movie_not_found"].format(code=code), parse_mode="Markdown")
        user_states[user_id] = {}
        return
        
    video_id, is_vip = movie
    
    if is_vip:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
        user_row = cursor.fetchone()
        conn.close()
        
        is_user_vip = user_row[0] if user_row else 0
        if not is_user_vip and user_id != ADMIN_ID:
            bot.send_message(m.chat.id, t["vip_only"])
            user_states[user_id] = {}
            return

    bot.send_video(m.chat.id, video_id, caption=f"🎬 Kino kodi: `{code}`", parse_mode="Markdown")
    user_states[user_id] = {}

def process_user_movie_request(chat_id, user_id, code):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]

    if user_id != ADMIN_ID and not check_channels_subscription(user_id):
        show_subscription_alert(chat_id, lang)
        return

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT video_id, is_vip FROM movies WHERE code = ?", (code,))
    movie = c
