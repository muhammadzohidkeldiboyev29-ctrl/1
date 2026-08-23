from datetime import datetime
import random
import sqlite3
import telebot
from telebot import types

TOKEN = "8816940858:AAEwDQ94ues00rcG1RVkNMPumQh7Xxgfowc"
ADMIN_ID = 8753350906
BOT_USERNAME = "Kinolarqbot"

bot = telebot.TeleBot(TOKEN)
user_states = {}
DB_NAME = "bot_database.db"

# --- MATNLAR LUG'ATI ---
LANG_TEXTS = {
    "uz": {
        "menu": "✅ Asosiy menyu:",
        "search_btn": "🔍 Qidirish",
        "random_btn": "🎲 Tasodifiy",
        "vip_btn": "💎 Premium Obuna",
        "lang_btn": "🌐 Tilni o'zgartirish",
        "ad_btn": "📢 Reklama",
        "suggest_btn": "💡 Kino tavsiya qilish",
        "stats_btn": "📊 Statistika",
        "broadcast_btn": "📢 Xabar yuborish (Reklama)",
        "add_movie_btn": "🎬 Kino yuklash",
        "status_btn": "🤖 Bot holati",
        "del_movie_btn": "🗑 Kino o'chirish",
        "edit_ad_btn": "⚙️ Reklamani o'zgartirish",
        "search_prompt": "🔎 Kino kodini yuboring (masalan: `1`):",
        "movie_not_found": "❌ `{code}` kodi topilmadi.",
        "movies_not_found": "❌ Kinolar topilmadi.",
        "download_count": "⬇️ Yuklangan:",
        "vip_text": (
            "💎 **VIP Premium Obuna narxlari:**\n\n🇺🇿 **O'zbekiston"
            " uchun:**\n• 1 oy — 15,000 so'm\n• 3 oy — 20,000 so'm\n• 6 oy —"
            " 35,000 so'm\n\n🇷🇺 **Для России (рубли):**\n• 1 месяц — 200 руб\n• 3"
            " месяца — 250 руб\n• 6 месяцев — 350 руб\n\n🇬🇧 **For English speakers"
            " (USD):**\n• 1 month — $12\n• 3 months — $15\n• 6 months —"
            " $22\n\n💳 Obuna bo'lish uchun adminga yozing: {contact}"
        ),
        "admin_add_video": (
            "🎬 Iltimos, bazaga qo'shmoqchi bo'lgan **kinoni (videoni)"
            " yuboring**:"
        ),
        "admin_video_ok": (
            "✅ Video qabul qilindi!\n\nEndi ushbu kino uchun **kod** yuboring"
            " (masalan: `12`):"
        ),
        "admin_saved": "🎉 Kino muvaffaqiyatli saqlandi!\n🎬 Kodi: `{code}`",
        "bot_status_ok": "🤖 Bot holati: Ajoyib ishlamoqda, server yoniq! ✅",
    },
    "ru": {
        "menu": "✅ Главное меню:",
        "search_btn": "🔍 Поиск",
        "random_btn": "🎲 Случайный",
        "vip_btn": "💎 VIP Подписка",
        "lang_btn": "🌐 Сменить язык",
        "ad_btn": "📢 Реклама",
        "suggest_btn": "💡 Предложить фильм",
        "stats_btn": "📊 Статистика",
        "broadcast_btn": "📢 Рассылка (Реклама)",
        "add_movie_btn": "🎬 Добавить фильм",
        "status_btn": "🤖 Статус бота",
        "del_movie_btn": "🗑 Удалить фильм",
        "edit_ad_btn": "⚙️ Изменить рекламу",
        "search_prompt": (
            "🔎 Отправьте код фильма или название (например: `1`):"
        ),
        "movie_not_found": "❌ Код `{code}` не найден.",
        "movies_not_found": "❌ Фильмы не найдены.",
        "download_count": "⬇️ Скачано:",
        "vip_text": (
            "💎 **Цены на VIP Премиум подписку:**\n\n🇺🇿 **Для Узбекистана:**\n•"
            " 1 месяц — 15,000 сум\n• 3 месяца — 20,000 сум\n• 6 месяцев —"
            " 35,000 сум\n\n🇷🇺 **Для России (рубли):**\n• 1 месяц — 200 руб\n• 3"
            " месяца — 250 руб\n• 6 месяцев — 350 руб\n\n🇬🇧 **For English speakers"
            " (USD):**\n• 1 month — $12\n• 3 months — $15\n• 6 months —"
            " $22\n\n💳 Для оформления подписки напишите админу: {contact}"
        ),
        "admin_add_video": (
            "🎬 Пожалуйста, **отправьте видео фильма**, который хотите добавить"
            " в базу:"
        ),
        "admin_video_ok": (
            "✅ Видео принято!\n\nТеперь отправьте **код** для этого фильма"
            " (например: `12`):"
        ),
        "admin_saved": "🎉 Фильм успешно сохранен!\n🎬 Код: `{code}`",
        "bot_status_ok": "🤖 Статус бота: Работает отлично, сервер активен! ✅",
    },
    "en": {
        "menu": "✅ Main menu:",
        "search_btn": "🔍 Search",
        "random_btn": "🎲 Random",
        "vip_btn": "💎 VIP Subscription",
        "lang_btn": "🌐 Change Language",
        "ad_btn": "📢 Ads",
        "suggest_btn": "💡 Suggest Movie",
        "stats_btn": "📊 Statistics",
        "broadcast_btn": "📢 Broadcast",
        "add_movie_btn": "🎬 Add Movie",
        "status_btn": "🤖 Bot Status",
        "del_movie_btn": "🗑 Delete Movie",
        "edit_ad_btn": "⚙️ Edit Ads",
        "search_prompt": "🔎 Send the movie code (e.g., `1`):",
        "movie_not_found": "❌ Code `{code}` not found.",
        "movies_not_found": "❌ No movies found.",
        "download_count": "⬇️ Downloads:",
        "vip_text": (
            "💎 **VIP Premium Subscription Pricing:**\n\n🇺🇿 **For"
            " Uzbekistan:**\n• 1 month — 15,000 sum\n• 3 months — 20,000 sum\n•"
            " 6 months — 35,000 sum\n\n🇷🇺 **For Russia (Rubles):**\n• 1"
            " month — 200 rub\n• 3 months — 250 rub\n• 6 months — 350"
            " rub\n\n🇬🇧 **For English speakers (USD):**\n• 1 month — $12\n• 3"
            " months — $15\n• 6 months — $22\n\n💳 To subscribe, contact the"
            " admin: {contact}"
        ),
        "admin_add_video": "🎬 Please send the **movie video** to add:",
        "admin_video_ok": (
            "✅ Video accepted!\n\nNow send the **code** for this movie (e.g.,"
            " `12`):"
        ),
        "admin_saved": "🎉 Movie successfully saved!\n🎬 Code: `{code}`",
        "bot_status_ok": "🤖 Bot Status: Working perfectly, server is online! ✅",
    },
}


def init_db():
  conn = sqlite3.connect(DB_NAME, check_same_thread=False)
  cursor = conn.cursor()
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username"
      " TEXT, lang TEXT DEFAULT 'uz', joined_date TEXT, is_vip INTEGER DEFAULT"
      " 0, vip_expire_date TEXT, is_banned INTEGER DEFAULT 0)"
  )
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, video_id TEXT,"
      " is_vip INTEGER DEFAULT 0, downloads INTEGER DEFAULT 0)"
  )
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"
  )
  conn.commit()

  cursor.execute(
      "INSERT OR IGNORE INTO settings (key, value) VALUES ('ad_username',"
      " '@reklamuchun1')"
  )
  cursor.execute(
      "INSERT OR IGNORE INTO settings (key, value) VALUES ('admin_contact',"
      " '@mhdnvwv')"
  )
  cursor.execute(
      "INSERT OR IGNORE INTO settings (key, value) VALUES ('ad_text', '🔥"
      " **ZAYAFKA KANALLARGA ZAKAZ OLAMAN!**\n\n👉 Jivoy, aktiv auditoriya\n⚡️"
      " Tez va sifatli ishlaymiz\n📈 Narxlar hamyonbop\n\n📞 Reklama va zakaz"
      " uchun lichkaga yozing: @mhdnvwv')"
  )
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


def show_main_menu(chat_id, user_id):
  lang = get_user_lang(user_id)
  t = LANG_TEXTS[lang]
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  markup.row(t["search_btn"], t["random_btn"])
  markup.row(t["vip_btn"], t["lang_btn"])
  markup.row(t["ad_btn"], t["suggest_btn"])

  if user_id == ADMIN_ID:
    markup.row(t["stats_btn"], t["broadcast_btn"])
    markup.row(t["add_movie_btn"], t["status_btn"])
    markup.row(t["del_movie_btn"], t["edit_ad_btn"])

  bot.send_message(chat_id, t["menu"], reply_markup=markup)


@bot.message_handler(commands=["start"])
def send_welcome(message):
  user_id = message.from_user.id
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO users (user_id, username, joined_date) VALUES (?,"
      " ?, ?)",
      (
          user_id,
          message.from_user.username,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      ),
  )
  conn.commit()
  conn.close()

  if message.text and message.text.startswith("/start kino_"):
    send_movie_by_code(message.chat.id, user_id, message.text.split("_")[1])
    return

  markup = types.InlineKeyboardMarkup()
  markup.row(
      types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
      types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
      types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
  )
  bot.send_message(
      message.chat.id,
      "🌍 Iltimos, tilni tanlang:\nПожалуйста, выберите язык:\nPlease select"
      " a language:",
      reply_markup=markup,
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def callback_language(call):
  lang = call.data.split("_")[1]
  set_user_lang(call.from_user.id, lang)
  bot.answer_callback_query(call.id, "Til saqlandi ✅")
  try:
    bot.delete_message(call.message.chat.id, call.message.message_id)
  except:
    pass
  show_main_menu(call.message.chat.id, call.from_user.id)


@bot.message_handler(
    func=lambda m: m.text
    in ["🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change Language"]
)
def change_lang_btn(m):
  markup = types.InlineKeyboardMarkup()
  markup.row(
      types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
      types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
      types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
  )
  bot.send_message(m.chat.id, "🌍 Tilni tanlang / Выберите язык:", reply_markup=markup)


@bot.message_handler(
    func=lambda m: m.text in ["💎 Premium Obuna", "💎 VIP Подписка", "💎 VIP Subscription"]
)
def vip_menu(m):
  lang = get_user_lang(m.from_user.id)
  admin_contact = get_setting("admin_contact")
  text = LANG_TEXTS[lang]["vip_text"].format(contact=admin_contact)
  bot.send_message(m.chat.id, text, parse_mode="Markdown")


@bot.message_handler(
    func=lambda m: m.text in ["📢 Reklama", "📢 Реклама", "📢 Ads"]
)
def ad_info(m):
  bot.send_message(m.chat.id, get_setting("ad_text"), parse_mode="Markdown")


@bot.message_handler(
    func=lambda m: m.from_user.id == ADMIN_ID
    and m.text
    in [
        "📊 Statistika",
        "📊 Статистика",
        "📊 Statistics",
        "🎬 Kino yuklash",
        "🎬 Добавить фильм",
        "🎬 Add Movie",
        "🤖 Bot holati",
        "🤖 Статус бота",
        "🤖 Bot Status",
    ]
)
def admin_actions(m):
  lang = get_user_lang(m.from_user.id)
  t = LANG_TEXTS[lang]

  if m.text in ["📊 Statistika", "📊 Статистика", "📊 Statistics"]:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    all_users = c.fetchall()

    total_users = len(all_users)
    active_users = 0
    blocked_users = 0

    # Faollar va chiqib ketganlarni tekshirish
    for (u_id,) in all_users:
      try:
        # Chat holatini so'rab ko'ramiz (agar botni bloklagan bo'lsa xato beradi)
        bot.send_chat_action(u_id, "typing")
        active_users += 1
      except:
        blocked_users += 1

    c.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
    vip_count = c.fetchone()[0]

    c.execute("SELECT SUM(downloads) FROM movies")
    total_downloads_row = c.fetchone()[0]
    total_downloads = total_downloads_row if total_downloads_row else 0

    c.execute("SELECT COUNT(*) FROM movies")
    total_movies = c.fetchone()[0]
    conn.close()

    stats_text = (
        f"📊 **Bot Statistikasi:**\n\n"
        f"👥 Jami obunachilar (baza): **{total_users} ta**\n"
        f"✅ Hozirda faollar: **{active_users} ta**\n"
        f"❌ Botni bloklaganlar (chiqib ketganlar): **{blocked_users} ta**\n"
        f"💎 VIP obunachilar: **{vip_count} ta**\n"
        f"🎬 Bazadagi kinolar: **{total_movies} ta**\n"
        f"⬇️ Jami video yuklanmalar: **{total_downloads} ta**"
    )
    bot.reply_to(m, stats_text, parse_mode="Markdown")

  elif m.text in ["🎬 Kino yuklash", "🎬 Добавить фильм", "🎬 Add Movie"]:
    user_states[m.from_user.id] = {"state": "waiting_for_movie"}
    bot.reply_to(m, t["admin_add_video"])

  elif m.text in ["🤖 Bot holati", "🤖 Статус бота", "🤖 Bot Status"]:
    bot.reply_to(m, t["bot_status_ok"])


@bot.message_handler(
    content_types=["video"],
    func=lambda m: m.from_user.id == ADMIN_ID
    and user_states.get(m.from_user.id, {}).get("state")
    == "waiting_for_movie",
)
def get_movie_video(m):
  lang = get_user_lang(m.from_user.id)
  video_id = m.video.file_id
  user_states[m.from_user.id] = {
      "state": "waiting_for_code",
      "video_id": video_id,
  }
  bot.reply_to(m, LANG_TEXTS[lang]["admin_video_ok"])


@bot.message_handler(
    func=lambda m: m.from_user.id == ADMIN_ID
    and user_states.get(m.from_user.id, {}).get("state")
    == "waiting_for_code"
)
def get_movie_code(m):
  lang = get_user_lang(m.from_user.id)
  code = m.text.strip()
  video_id = user_states[m.from_user.id].get("video_id")

  conn = get_db()
  cursor = conn.cursor()
  try:
    cursor.execute(
        "INSERT OR REPLACE INTO movies (code, video_id, is_vip, downloads)"
        " VALUES (?, ?, 0, 0)",
        (code, video_id),
    )
    conn.commit()
    conn.close()
    bot.reply_to(
        m,
        LANG_TEXTS[lang]["admin_saved"].format(code=code),
        parse_mode="Markdown",
    )
  except Exception as e:
    bot.reply_to(m, f"❌ Error: {e}")
  user_states[m.from_user.id] = {}


@bot.message_handler(
    func=lambda m: m.text in ["🎲 Tasodifiy", "🎲 Случайный", "🎲 Random"]
)
def random_m(message):
  user_id = message.from_user.id
  lang = get_user_lang(user_id)
  t = LANG_TEXTS[lang]

  conn = get_db()
  c = conn.cursor()
  c.execute("SELECT code, video_id, downloads FROM movies")
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

  admin_contact = get_setting("admin_contact")
  ad_username = get_setting("ad_username").replace("@", "")

  markup = types.InlineKeyboardMarkup()
  markup.row(
      types.InlineKeyboardButton("📢 Reklama", url=f"https://t.me/{ad_username}"),
      types.InlineKeyboardButton(
          "💎 VIP Obuna", url=f"https://t.me/{admin_contact.replace('@', '')}"
      ),
  )

  caption = (
      f"🎬 Kod: `{code}`\n\n{get_setting('ad_text')}\n\n{t['download_count']}"
      f" {downloads + 1}"
  )
  bot.send_video(
      message.chat.id,
      video_id,
      caption=caption,
      parse_mode="Markdown",
      reply_markup=markup,
  )


@bot.message_handler(
    func=lambda m: m.text in ["🔍 Qidirish", "🔍 Поиск", "🔍 Search"]
)
def search(m):
  lang = get_user_lang(m.from_user.id)
  bot.send_message(m.chat.id, LANG_TEXTS[lang]["search_prompt"])


@bot.message_handler(
    func=lambda m: m.text
    and not m.text.startswith("/")
    and m.text
    not in [
        "📊 Statistika",
        "📊 Статистика",
        "📊 Statistics",
        "🎲 Tasodifiy",
        "🎲 Случайный",
        "🎲 Random",
        "🔍 Qidirish",
        "🔍 Поиск",
        "🔍 Search",
        "💎 Premium Obuna",
        "💎 VIP Подписка",
        "💎 VIP Subscription",
        "📢 Reklama",
        "📢 Реклама",
        "📢 Ads",
        "🌐 Tilni o'zgartirish",
        "🌐 Сменить язык",
        "🌐 Change Language",
        "💡 Kino tavsiya qilish",
        "💡 Предложить фильм",
        "💡 Suggest Movie",
        "🎬 Kino yuklash",
        "🎬 Добавить фильм",
        "🎬 Add Movie",
        "🤖 Bot holati",
        "🤖 Статус бота",
        "🤖 Bot Status",
        "🗑 Kino o'chirish",
        "⚙️ Reklamani o'zgartirish",
    ]
)
def handle_text_codes(message):
  code = message.text.strip()
  send_movie_by_code(message.chat.id, message.from_user.id, code)


def send_movie_by_code(chat_id, user_id, code):
  lang = get_user_lang(user_id)
  t = LANG_TEXTS[lang]

  conn = get_db()
  c = conn.cursor()
  c.execute(
      "SELECT video_id, is_vip, downloads FROM movies WHERE code = ?", (code,)
  )
  movie = c.fetchone()
  conn.close()

  if not movie:
    bot.send_message(
        chat_id, t["movie_not_found"].format(code=code), parse_mode="Markdown"
    )
    return

  video_id, is_vip, downloads = movie

  conn = get_db()
  c = conn.cursor()
  c.execute("UPDATE movies SET downloads = downloads + 1 WHERE code = ?", (code,))
  conn.commit()
  conn.close()

  admin_contact = get_setting("admin_contact")
  ad_username = get_setting("ad_username").replace("@", "")

  markup = types.InlineKeyboardMarkup()
  markup.row(
      types.InlineKeyboardButton("📢 Reklama", url=f"https://t.me/{ad_username}"),
      types.InlineKeyboardButton(
          "💎 VIP Obuna", url=f"https://t.me/{admin_contact.replace('@', '')}"
      ),
  )

  caption = (
      f"🎬 Kod: `{code}`\n\n{get_setting('ad_text')}\n\n{t['download_count']}"
      f" {downloads + 1}"
  )
  bot.send_video(
      chat_id,
      video_id,
      caption=caption,
      parse_mode="Markdown",
      reply_markup=markup,
  )


if __name__ == "__main__":
  bot.infinity_polling()
  
