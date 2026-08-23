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
        "add_movie_btn": "🎬 Oddiy kino qo'shish",
        "add_vip_movie_btn": "💎 VIP kino qo'shish",
        "status_btn": "🤖 Bot holati",
        "del_movie_btn": "🗑 Kino o'chirish",
        "edit_ad_btn": "⚙️ Reklamani o'zgartirish",
        "channels_btn": "📢 Kanallarni sozlash",
        "add_channel_btn": "➕ Kanal qo'shish",
        "del_channel_btn": "🗑 Kanalni o'chirish",
        "remove_vip_btn": "🚫 VIP'dan chiqarish",
        "search_prompt": "🔎 Kino kodini yuboring (masalan: `1`):",
        "movie_not_found": "❌ `{code}` kodi topilmadi.",
        "movies_not_found": "❌ Kinolar topilmadi.",
        "download_count": "⬇️ Yuklangan:",
        "vip_choose_period": (
            "💎 **VIP Premium Obuna**\n\nIltimos, obuna muddatini tanlang:"
        ),
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
        "add_movie_btn": "🎬 Добавить обычный фильм",
        "add_vip_movie_btn": "💎 Добавить VIP фильм",
        "status_btn": "🤖 Статус бота",
        "del_movie_btn": "🗑 Удалить фильм",
        "edit_ad_btn": "⚙️ Изменить рекламу",
        "channels_btn": "📢 Настройка каналов",
        "add_channel_btn": "➕ Добавить канал",
        "del_channel_btn": "🗑 Удалить канал",
        "remove_vip_btn": "🚫 Убрать с VIP",
        "search_prompt": (
            "🔎 Отправьте код фильма или название (например: `1`):"
        ),
        "movie_not_found": "❌ Код `{code}` не найден.",
        "movies_not_found": "❌ Фильмы не найдены.",
        "download_count": "⬇️ Скачано:",
        "vip_choose_period": (
            "💎 **VIP Премиум Подписка**\n\nПожалуйста, выберите срок подписки:"
        ),
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
        "add_movie_btn": "🎬 Add Regular Movie",
        "add_vip_movie_btn": "💎 Add VIP Movie",
        "status_btn": "🤖 Bot Status",
        "del_movie_btn": "🗑 Delete Movie",
        "edit_ad_btn": "⚙️ Edit Ads",
        "channels_btn": "📢 Channels Setup",
        "add_channel_btn": "➕ Add Channel",
        "del_channel_btn": "🗑 Delete Channel",
        "remove_vip_btn": "🚫 Remove VIP",
        "search_prompt": "🔎 Send the movie code (e.g., `1`):",
        "movie_not_found": "❌ Code `{code}` not found.",
        "movies_not_found": "❌ No movies found.",
        "download_count": "⬇️ Downloads:",
        "vip_choose_period": (
            "💎 **VIP Premium Subscription**\n\nPlease select the subscription"
            " period:"
        ),
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
      "INSERT OR IGNORE INTO settings (key, value) VALUES ('card_number',"
      " '6262 5701 4806 4381 (Obidjonova M)')"
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


def show_vip_keyboard(lang):
  markup = types.InlineKeyboardMarkup()
  if lang == "uz":
    markup.row(
        types.InlineKeyboardButton("1 oy — 15,000 so'm", callback_data="vip_uz_1")
    )
    markup.row(
        types.InlineKeyboardButton("3 oy — 20,000 so'm", callback_data="vip_uz_3")
    )
    markup.row(
        types.InlineKeyboardButton(
            "6 oy — 35,000 so'm", callback_data="vip_uz_6"
        )
    )
  elif lang == "ru":
    markup.row(
        types.InlineKeyboardButton(
            "1 месяц — 200 руб", callback_data="vip_ru_1"
        )
    )
    markup.row(
        types.InlineKeyboardButton(
            "3 месяца — 250 руб", callback_data="vip_ru_3"
        )
    )
    markup.row(
        types.InlineKeyboardButton(
            "6 месяцев — 350 руб", callback_data="vip_ru_6"
        )
    )
  else:
    markup.row(
        types.InlineKeyboardButton("1 month — $12", callback_data="vip_en_1")
    )
    markup.row(
        types.InlineKeyboardButton("3 months — $15", callback_data="vip_en_3")
    )
    markup.row(
        types.InlineKeyboardButton("6 months — $22", callback_data="vip_en_6")
    )
  return markup


def show_main_menu(chat_id, user_id):
  lang = get_user_lang(user_id)
  t = LANG_TEXTS[lang]
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  markup.row(t["search_btn"], t["random_btn"])
  markup.row(t["vip_btn"], t["lang_btn"])
  markup.row(t["ad_btn"], t["suggest_btn"])

  if user_id == ADMIN_ID:
    markup.row(t["stats_btn"], t["broadcast_btn"])
    markup.row(t["add_movie_btn"], t["add_vip_movie_btn"])
    markup.row(t["channels_btn"], t["add_channel_btn"])
    markup.row(t["del_channel_btn"], t["remove_vip_btn"])
    markup.row(t["status_btn"], t["edit_ad_btn"])
    markup.row(t["del_movie_btn"])

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
  t = LANG_TEXTS[lang]
  markup = show_vip_keyboard(lang)
  bot.send_message(m.chat.id, t["vip_choose_period"], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("vip_"))
def callback_vip_period(call):
  parts = call.data.split("_")
  lang = parts[1]
  period = parts[2]

  card = get_setting("card_number")
  prices = {
      "uz": {"1": "15,000 so'm", "3": "20,000 so'm", "6": "35,000 so'm"},
      "ru": {"1": "200 руб", "3": "250 руб", "6": "350 руб"},
      "en": {"1": "$12", "3": "$15", "6": "$22"},
  }
  price = prices[lang][period]

  if lang == "uz":
    text = (
        f"💎 **Siz {period} oylik VIP obunani tanladingiz.**\nNarxi: **{price}"
        f"**\n\n💳 Karta va egasi:\n`{card}`\n\nTo'lovni amalga oshirgach,"
        " to'lov chekini (screenshot) shu botga yuboring! Bot uni adminga"
        " yuboradi."
    )
  elif lang == "ru":
    text = (
        f"💎 **Вы выбрали VIP подписку на {period} мес.**\nЦена:"
        f" **{price}**\n\n💳 Карта и владелец:\n`{card}`\n\nПосле оплаты отправьте"
        " скриншот чека в этот бот!"
    )
  else:
    text = (
        f"💎 **You selected VIP subscription for {period}"
        f" month(s).**\nPrice: **{price}**\n\n💳 Card & Owner:\n`{card}`\n\nAfter"
        " payment, send the screenshot to this bot!"
    )

  bot.answer_callback_query(call.id)
  bot.send_message(call.message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(
    content_types=["photo"],
    func=lambda m: m.from_user.id != ADMIN_ID and m.caption in [None, ""],
)
def handle_payment_screenshot(message):
  user_id = message.from_user.id
  username = (
      f"@{message.from_user.username}"
      if message.from_user.username
      else f"ID: {user_id}"
  )
  photo_id = message.photo[-1].file_id

  markup = types.InlineKeyboardMarkup()
  markup.row(
      types.InlineKeyboardButton(
          "✅ Tasdiqlash", callback_data=f"accept_vip_{user_id}"
      ),
      types.InlineKeyboardButton(
          "❌ Rad etish", callback_data=f"reject_vip_{user_id}"
      ),
  )

  bot.send_photo(
      ADMIN_ID,
      photo_id,
      caption=(
          f"💳 **Yangi to'lov cheki keldi!**\n\nFoydalanuvchi: {username}\nID:"
          f" `{user_id}`"
      ),
      parse_mode="Markdown",
      reply_markup=markup,
  )
  bot.reply_to(
      message,
      "✅ Chekingiz adminga yuborildi! Admin tekshirib chiqishi bilan"
      " obunangiz faollashadi.",
  )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("accept_vip_")
    or call.data.startswith("reject_vip_")
)
def admin_vip_decision(call):
  if call.from_user.id != ADMIN_ID:
    return

  data = call.data.split("_")
  action = data[0]
  user_id = int(data[2])

  if action == "accept":
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    bot.answer_callback_query(call.id, "Obuna tasdiqlandi ✅")
    bot.send_message(
        user_id,
        "🎉 Tabriklaymiz! Admin sizning to'lovingizni tasdiqladi va VIP"
        " obunani yoqdi! ✅",
    )
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=call.message.caption + "\n\n✅ **HOLATI: TASDIQLANGAN**",
        parse_mode="Markdown",
    )
  else:
    bot.answer_callback_query(call.id, "Obuna rad etildi ❌")
    bot.send_message(
        user_id,
        "❌ Afsuski, admin to'lov chekingizni rad etdi (soxta yoki xato"
        " summa).",
    )
    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=call.message.caption + "\n\n❌ **HOLATI: RAD ETILGAN**",
        parse_mode="Markdown",
    )


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
        "🎬 Oddiy kino qo'shish",
        "🎬 Добавить обычный фильм",
        "🎬 Add Regular Movie",
        "💎 VIP kino qo'shish",
        "💎 Добавить VIP фильм",
        "💎 Add VIP Movie",
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

    for (u_id,) in all_users:
      try:
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

  elif m.text in [
      "🎬 Oddiy kino qo'shish",
      "🎬 Добавить обычный фильм",
      "🎬 Add Regular Movie",
  ]:
    user_states[m.from_user.id] = {"state": "waiting_for_movie", "is_vip": 0}
    bot.reply_to(m, "🎬 Iltimos, bazaga qo'shmoqchi bo'lgan **oddiy kinoni** yuboring:")

  elif m.text in [
      "💎 VIP kino qo'shish",
      "💎 Добавить VIP фильм",
      "💎 Add VIP Movie",
  ]:
    user_states[m.from_user.id] = {"state": "waiting_for_movie", "is_vip": 1}
    bot.reply_to(m, "💎 Iltimos, bazaga qo'shmoqchi bo'lgan **VIP kinoni** yuboring:")

  elif m.text in ["🤖 Bot holati", "🤖 Статус бота", "🤖 Bot Status"]:
    bot.reply_to(m, t["bot_status_ok"])


@bot.message_handler(
    content_types=["video"],
    func=lambda m: m.from_user.id == ADMIN_ID
    and user_states.get(m.from_user.id, {}).get("state")
    == "waiting_for_movie",
)
def get_movie_video(m):
  video_id = m.video.file_id
  is_vip = user_states[m.from_user.id].get("is_vip", 0)
  user_states[m.from_user.id] = {
      "state": "waiting_for_code",
      "video_id": video_id,
      "is_vip": is_vip,
  }
  bot.reply_to(
      m,
      "✅ Video qabul qilindi!\n\nEndi ushbu kino uchun **kod** yuboring (masalan:"
      " `12`):",
  )


@bot.message_handler(
    func=lambda m: m.from_user.id == ADMIN_ID
    and user_states.get(m.from_user.id, {}).get("state")
    == "waiting_for_code"
)
def get_movie_code(m):
  code = m.text.strip()
  state_data = user_states.get(m.from_user.id, {})
  video_id = state_data.get("video_id")
  is_vip = state_data.get("is_vip", 0)

  conn = get_db()
  cursor = conn.cursor()
  try:
    cursor.execute(
        "INSERT OR REPLACE INTO movies (code, video_id, is_vip, downloads)"
        " VALUES (?, ?, ?, 0)",
        (code, video_id, is_vip),
    )
    conn.commit()
    conn.close()
    movie_type = "💎 VIP kino" if is_vip == 1 else "🎬 Oddiy kino"
    bot.reply_to(
        m,
        f"🎉 {movie_type} muvaffaqiyatli saqlandi!\nKodi: `{code}`",
        parse_mode="Markdown",
    )
  except Exception as e:
    bot.reply_to(m, f"❌ Xatolik: {e}")
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
  c.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
  user_vip_row = c.fetchone()
  is_user_vip = user_vip_row[0] if user_vip_row else 0

  if is_user_vip:
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
        "💎 Premium Ob
