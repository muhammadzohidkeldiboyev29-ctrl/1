from datetime import datetime
import random
import sqlite3
import telebot
from telebot import types

TOKEN = "8816940858:AAF2AdMub0XRMqBOYeyyPyjNbwZDShjEy9o"
ADMIN_ID = 8753350906
BOT_USERNAME = "Kinolarqbot"

bot = telebot.TeleBot(TOKEN)
user_states = {}
DB_NAME = "bot_database.db"

LANG_TEXTS = {
    "uz": {
        "menu": "✅ Asosiy menyu:",
        "search_btn": "🔍 Qidirish",
        "random_btn": "🎲 Tasodifiy",
        "vip_btn": "💎 Premium Obuna",
        "lang_btn": "🌐 Tilni o'zgartirish",
        "ad_btn": "📢 Reklama",
        "stats_btn": "📊 Statistika",
        "add_movie_btn": "🎬 Kino qo'shish",
        "add_vip_movie_btn": "💎 VIP kino qo'shish",
        "status_btn": "🤖 Bot holati",
        "del_movie_btn": "🗑 O'chirish",
        "search_prompt": "🔎 Kino kodini yuboring (masalan: `1`):",
        "movie_not_found": "❌ `{code}` kodi topilmadi.",
        "movies_not_found": "❌ Kinolar topilmadi.",
        "download_count": "⬇️ Yuklangan:",
        "vip_choose_period": "💎 **VIP Premium Obuna**\n\nMuddatni tanlang:",
        "bot_status_ok": "🤖 Bot holati: Ajoyib ishlamoqda ✅"
    },
    "ru": {
        "menu": "✅ Главное меню:",
        "search_btn": "🔍 Поиск",
        "random_btn": "🎲 Случайный",
        "vip_btn": "💎 VIP Подписка",
        "lang_btn": "🌐 Сменить язык",
        "ad_btn": "📢 Реклама",
        "stats_btn": "📊 Статистика",
        "add_movie_btn": "🎬 Добавить фильм",
        "add_vip_movie_btn": "💎 Добавить VIP",
        "status_btn": "🤖 Статус бота",
        "del_movie_btn": "🗑 Удалить",
        "search_prompt": "🔎 Отправьте код фильма (например: `1`):",
        "movie_not_found": "❌ Код `{code}` не найден.",
        "movies_not_found": "❌ Фильмы не найдены.",
        "download_count": "⬇️ Скачано:",
        "vip_choose_period": "💎 **VIP Премиум Подписка**\n\nВыберите срок:",
        "bot_status_ok": "🤖 Статус бота: Работает отлично ✅"
    },
    "en": {
        "menu": "✅ Main menu:",
        "search_btn": "🔍 Search",
        "random_btn": "🎲 Random",
        "vip_btn": "💎 VIP Subscription",
        "lang_btn": "🌐 Language",
        "ad_btn": "📢 Ads",
        "stats_btn": "📊 Statistics",
        "add_movie_btn": "🎬 Add Movie",
        "add_vip_movie_btn": "💎 Add VIP",
        "status_btn": "🤖 Bot Status",
        "del_movie_btn": "🗑 Delete",
        "search_prompt": "🔎 Send movie code (e.g., `1`):",
        "movie_not_found": "❌ Code `{code}` not found.",
        "movies_not_found": "❌ No movies found.",
        "download_count": "⬇️ Downloads:",
        "vip_choose_period": "💎 **VIP Premium Subscription**\n\nSelect period:",
        "bot_status_ok": "🤖 Bot Status: Working perfectly ✅"
    }
}

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, lang TEXT DEFAULT 'uz', joined_date TEXT, is_vip INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, video_id TEXT, is_vip INTEGER DEFAULT 0, downloads INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    conn.commit()
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('ad_username', '@reklamuchun1')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_contact', '@mhdnvwv')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('card_number', '6262 5701 4806 4381 (Obidjonova M)')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('ad_text', '🔥 **REKLAMA JOYI**\\n\\nMurojaat uchun: @mhdnvwv')")
    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def get_setting(key):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

def set_setting(key, value):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

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

def show_vip_keyboard(lang):
    markup = types.InlineKeyboardMarkup()
    if lang == 'uz':
        markup.row(types.InlineKeyboardButton("1 oy — 15,000 so'm", callback_data="vip_uz_1"))
        markup.row(types.InlineKeyboardButton("3 oy — 20,000 so'm", callback_data="vip_uz_3"))
        markup.row(types.InlineKeyboardButton("6 oy — 35,000 so'm", callback_data="vip_uz_6"))
    elif lang == 'ru':
        markup.row(types.InlineKeyboardButton("1 месяц — 200 руб", callback_data="vip_ru_1"))
        markup.row(types.InlineKeyboardButton("3 месяца — 250 руб", callback_data="vip_ru_3"))
        markup.row(types.InlineKeyboardButton("6 месяцев — 450 руб", callback_data="vip_ru_6"))
    else:
        markup.row(types.InlineKeyboardButton("1 month — $12", callback_data="vip_en_1"))
        markup.row(types.InlineKeyboardButton("3 months — $15", callback_data="vip_en_3"))
        markup.row(types.InlineKeyboardButton("6 months — $25", callback_data="vip_en_6"))
    return markup

def show_main_menu(chat_id, user_id):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(t["search_btn"], t["random_btn"])
    markup.row(t["vip_btn"], t["lang_btn"])
    markup.row(t["ad_btn"])
    
    if user_id == ADMIN_ID:
        markup.row(t["stats_btn"], t["status_btn"])
        markup.row(t["add_movie_btn"], t["add_vip_movie_btn"])
        markup.row(t["del_movie_btn"])
        
    bot.send_message(chat_id, t["menu"], reply_markup=markup)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, joined_date) VALUES (?, ?, ?)", (user_id, message.from_user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    
    if message.text and message.text.startswith('/start kino_'):
        send_movie_by_code(message.chat.id, user_id, message.text.split('_')[1])
        return

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(message.chat.id, "🌍 Tilni tanlang / Выберите язык:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def callback_language(call):
    lang = call.data.split('_')[1]
    set_user_lang(call.from_user.id, lang)
    bot.answer_callback_query(call.id, "Saved ✅")
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    show_main_menu(call.message.chat.id, call.from_user.id)

@bot.message_handler(func=lambda m: m.text in ["🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Language"])
def change_lang_btn(m):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(m.chat.id, "🌍 Tilni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["💎 Premium Obuna", "💎 VIP Подписка", "💎 VIP Subscription"])
def vip_menu(m):
    lang = get_user_lang(m.from_user.id)
    t = LANG_TEXTS[lang]
    markup = show_vip_keyboard(lang)
    bot.send_message(m.chat.id, t["vip_choose_period"], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('vip_'))
def callback_vip_period(call):
    parts = call.data.split('_')
    lang = parts[1]
    period = parts[2]
    card = get_setting('card_number')
    text = f"💎 **VIP obuna ({period} oy)**\n\n💳 Karta: `{card}`\n\nTo'lov chekini shu yerga yuboring!"
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
    bot.send_photo(ADMIN_ID, photo_id, caption=f"💳 **Yangi chek!**\nUser ID: `{user_id}`", parse_mode="Markdown", reply_markup=markup)
    bot.reply_to(message, "✅ Chek admingacha yetib bordi!")

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
        bot.send_message(user_id, "🎉 VIP obunangiz faollashdi! ✅")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n✅ TASDIQLANGAN")
    else:
        bot.answer_callback_query(call.id, "Rad etildi ❌")
        bot.send_message(user_id, "❌ To'lov cheki rad etildi.")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + "\n\n❌ RAD ETILGAN")

@bot.message_handler(func=lambda m: m.text in ["📢 Reklama", "📢 Реклама", "📢 Ads"])
def ad_info(m):
    bot.send_message(m.chat.id, get_setting('ad_text'), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text in [
    "📊 Statistika", "📊 Статистика", "📊 Statistics",
    "🎬 Kino qo'shish", "🎬 Добавить фильм", "🎬 Add Movie",
    "💎 VIP kino qo'shish", "💎 Добавить VIP", "💎 Add VIP",
    "🤖 Bot holati", "🤖 Статус бота", "🤖 Bot Status",
    "🗑 O'chirish"
])
def admin_actions(m):
    lang = get_user_lang(m.from_user.id)
    t = LANG_TEXTS[lang]
    
    if "Statistika" in m.text or "Статистика" in m.text or "Statistics" in m.text:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        u_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
        v_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM movies")
        m_count = c.fetchone()[0]
        conn.close()
        bot.reply_to(m, f"📊 Statistika:\n👥 Userlar: {u_count}\n💎 VIP: {v_count}\n🎬 Kinolar: {m_count}")
    elif "Kino qo'shish" in m.text or "Добавить фильм" in m.text or "Add Movie" in m.text:
        user_states[m.from_user.id] = {'state': 'waiting_for_movie', 'is_vip': 0}
        bot.reply_to(m, "🎬 Oddiy kino videosini yuboring:")
    elif "VIP kino" in m.text or "Добавить VIP" in m.text:
        user_states[m.from_user.id] = {'state': 'waiting_for_movie', 'is_vip': 1}
        bot.reply_to(m, "💎 VIP kino videosini yuboring:")
    elif "Bot holati" in m.text or "Статус" in m.text:
        bot.reply_to(m, t["bot_status_ok"])
    elif "O'chirish" in m.text:
        user_states[m.from_user.id] = {'state': 'waiting_for_del_code'}
        bot.reply_to(m, "🗑 O'chirilishi kerak bo'lgan kino kodini yuboring:")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_del_code')
def delete_movie(m):
    code = m.text.strip()
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM movies WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    bot.reply_to(m, f"🗑 `{code}` kodi o'chirildi!", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(content_types=['video'], func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_movie')
def get_movie_video(m):
    user_states[m.from_user.id]['video_id'] = m.video.file_id
    user_states[m.from_user.id]['state'] = 'waiting_for_code'
    bot.reply_to(m, "✅ Video qabul qilindi. Endi kod yuboring (masalan: `1`):")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and user_states.get(m.from_user.id, {}).get('state') == 'waiting_for_code')
def get_movie_code(m):
    code = m.text.strip()
    data = user_states.get(m.from_user.id, {})
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO movies (code, video_id, is_vip, downloads) VALUES (?, ?, ?, 0)", (code, data.get('video_id'), data.get('is_vip', 0)))
    conn.commit()
    conn.close()
    bot.reply_to(m, f"🎉 Saqlandi! Kodi: `{code}`", parse_mode="Markdown")
    user_states[m.from_user.id] = {}

@bot.message_handler(func=lambda m: m.text in ["🎲 Tasodifiy", "🎲 Случайный", "🎲 Random"])
def random_m(message):
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    is_vip = row[0] if row else 0
    
    if is_vip:
        c.execute("SELECT code, video_id, downloads FROM movies")
    else:
        c.execute("SELECT code, video_id, downloads FROM movies WHERE is_vip = 0")
    movies = c.fetchall()
    conn.close()
    
    if not movies:
        bot.send_message(message.chat.id, t["movies_not_found"])
        return
    code, video_id, downloads = random.choice(movies)
    
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE movies SET downloads = downloads + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    
    caption = f"🎬 Kod: `{code}`\n\n{t['download_count']} {downloads + 1}\n\n💬 Murojaat va jonli obzorlar uchun: @mhdnvwv"
    bot.send_video(message.chat.id, video_id, caption=caption, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["🔍 Qidirish", "🔍 Поиск", "🔍 Search"])
def search(m):
    lang = get_user_lang(m.from_user.id)
    bot.send_message(m.chat.id, LANG_TEXTS[lang]["search_prompt"])

EXCLUDED_BTNS = [
    "📊 Statistika", "📊 Статистика", "📊 Statistics", "🎲 Tasodifiy", "🎲 Случайный", "🎲 Random",
    "🔍 Qidirish", "🔍 Поиск", "🔍 Search", "💎 Premium Obuna", "💎 VIP Подписка", "💎 VIP Subscription",
    "📢 Reklama", "📢 Реклама", "📢 Ads", "🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Language",
    "🎬 Kino qo'shish", "💎 VIP kino qo'shish", "🤖 Bot holati", "🤖 Статус бота", "🤖 Bot Status", "🗑 O'chirish"
]

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/') and m.text not in EXCLUDED_BTNS)
def handle_text_codes(message):
    send_movie_by_code(message.chat.id, message.from_user.id, message.text.strip())

def send_movie_by_code(chat_id, user_id, code):
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT video_id, is_vip, downloads FROM movies WHERE code = ?", (code,))
    movie = c.fetchone()
    c.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
    u_row = c.fetchone()
    conn.close()
    
    if not movie:
        bot.send_message(chat_id, t["movie_not_found"].format(code=code), parse_mode="Markdown")
        return
        
    video_id, is_vip, downloads = movie
    is_user_vip = u_row[0] if u_row else 0
    
    if is_vip == 1 and is_user_vip == 0 and user_id != ADMIN_ID:
        markup = show_vip_keyboard(lang)
        bot.send_message(chat_id, "❌ Bu kino faqat VIP obunachilar uchun!", reply_markup=markup)
        return
        
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE movies SET downloads = downloads + 1 WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    
    caption = f"🎬 Kod: `{code}`\n\n{t['download_count']} {downloads + 1}\n\n💬 Murojaat va jonli obzorlar uchun: @mhdnvwv"
    bot.send_video(chat_id, video_id, caption=caption, parse_mode="Markdown")

if __name__ == "__main__":
    bot.infinity_polling()
