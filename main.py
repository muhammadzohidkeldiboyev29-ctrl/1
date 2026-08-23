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


def init_db():
  conn = sqlite3.connect(DB_NAME, check_same_thread=False)
  cursor = conn.cursor()
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username"
      " TEXT, joined_date TEXT, is_vip INTEGER DEFAULT 0, vip_expire_date TEXT,"
      " is_banned INTEGER DEFAULT 0)"
  )
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, video_id TEXT,"
      " is_vip INTEGER DEFAULT 0, downloads INTEGER DEFAULT 0)"
  )
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS channels (channel_username TEXT PRIMARY KEY)"
  )
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)"
  )
  conn.commit()
  cursor.execute(
      "INSERT OR IGNORE INTO settings (key, value) VALUES ('ad_username',"
      " '@reklamuchun1')"
  )
  conn.commit()
  cursor.execute(
      "INSERT OR IGNORE INTO settings (key, value) VALUES ('ad_text', '🔥"
      " **ZAYAFKA KANALLARGA ZAKAZ OLAMAN!**\n\nKanalga odam kerakmi? Unda yozing"
      " ↘️👇 Jivoy, aktiv auditoriya\n⚡️ Tez va sifatli ishlaymiz\n📈 Narxlar"
      " hamyonbop\n\n👉 Zakaz uchun lichkaga yozing')"
  )
  conn.commit()
  cursor.execute("SELECT COUNT(*) FROM channels")
  if cursor.fetchone()[0] == 0:
    for ch in ["@max_films01", "@reklamuchun1", "@sevshgnrlr"]:
      cursor.execute(
          "INSERT OR IGNORE INTO channels (channel_username) VALUES (?)", (ch,)
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


def set_setting(key, value):
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value)
  )
  conn.commit()
  conn.close()


def get_current_channels():
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute("SELECT channel_username FROM channels")
  rows = cursor.fetchall()
  conn.close()
  return [row[0] for row in rows]


def check_sub(user_id):
  if user_id == ADMIN_ID:
    return True
  for ch in get_current_channels():
    try:
      status = bot.get_chat_member(ch, user_id).status
      if status not in ["member", "administrator", "creator"]:
        return False
    except:
      return False
  return True


def is_user_vip(user_id):
  if user_id == ADMIN_ID:
    return True
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute(
      "SELECT is_vip, vip_expire_date FROM users WHERE user_id = ?", (user_id,)
  )
  row = cursor.fetchone()
  conn.close()
  if not row:
    return False
  is_vip, expire_date_str = row
  if is_vip == 1 and expire_date_str:
    if datetime.now() > datetime.strptime(
        expire_date_str, "%Y-%m-%d %H:%M:%S"
    ):
      conn = get_db()
      cursor = conn.cursor()
      cursor.execute(
          "UPDATE users SET is_vip = 0, vip_expire_date = NULL WHERE user_id"
          " = ?",
          (user_id,),
      )
      conn.commit()
      conn.close()
      return False
    return True
  return is_vip == 1


def is_user_banned(user_id):
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
  row = cursor.fetchone()
  conn.close()
  return row[0] == 1 if row else False


def show_main_menu(chat_id, user_id):
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  markup.row("🔍 Qidirish", "🎲 Tasodifiy")
  markup.row("💡 Kino tavsiya qilish", "📬 Shaxsiy kino qo'shish")
  markup.row("🎬 Admin orqali kino qo'shish", "💎 Premium Obuna")
  markup.row("📢 Reklama")
  if user_id == ADMIN_ID:
    markup.row("📊 Statistika", "📢 Xabar yuborish (Reklama)")
    markup.row("🎬 Kino yuklash", "🤖 Bot holati")
    markup.row("📢 Kanallarni sozlash", "➕ Kanal qo'shish")
    markup.row("🗑 Kanalni o'chirish", "⚙️ Reklamani o'zgartirish")
    markup.row("🚫 VIP'dan chiqarish", "🗑 Kino o'chirish")
  bot.send_message(chat_id, "✅ Asosiy menyu:", reply_markup=markup)


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

  if is_user_banned(user_id):
    bot.send_message(message.chat.id, "❌ Siz botdan bloklangansiz!")
    return

  if not is_user_vip(user_id) and not check_sub(user_id):
    markup = types.InlineKeyboardMarkup()
    for ch in get_current_channels():
      markup.add(
          types.InlineKeyboardButton(
              "📢 Kanalga o'tish",
              url=f"https://t.me/{ch.replace('@', '')}",
          )
      )
    markup.add(
        types.InlineKeyboardButton(
            "🔄 Tekshirish", callback_data="check_subscription"
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            "💎 Premium Obuna", callback_data="btn_vip_menu"
        )
    )
    bot.send_message(
        message.chat.id,
        "✨ Botdan foydalanish uchun kanallarga obuna bo'ling:",
        reply_markup=markup,
    )
    return

  if message.text and message.text.startswith("/start kino_"):
    send_movie_by_code(message.chat.id, user_id, message.text.split("_")[1])
    return
  show_main_menu(message.chat.id, user_id)


@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def callback_sub(call):
  if check_sub(call.from_user.id):
    bot.answer_callback_query(call.id, "Rahmat! Obuna tasdiqlandi ✅")
    try:
      bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
      pass
    show_main_menu(call.message.chat.id, call.from_user.id)
  else:
    bot.answer_callback_query(
        call.id, "Siz hali hamma kanallarga a'zo bo'lmadingiz! ❌", show_alert=True
    )


@bot.message_handler(
    func=lambda m: m.text == "📊 Statistika" and m.from_user.id == ADMIN_ID
)
def stats(m):
  conn = get_db()
  c = conn.cursor()
  c.execute("SELECT COUNT(*) FROM users")
  u = c.fetchone()[0]
  c.execute("SELECT COUNT(*) FROM movies")
  mv = c.fetchone()[0]
  c.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
  v = c.fetchone()[0]
  conn.close()
  bot.reply_to(
      m,
      f"📊 Statistika:\nFoydalanuvchilar: {u}\nVIP'lar: {v}\nKinolar: {mv}",
  )


@bot.message_handler(
    func=lambda m: m.text == "🎲 Tasodifiy"
)
def random_m(message):
  conn = get_db()
  c = conn.cursor()
  if is_user_vip(message.from_user.id):
    c.execute("SELECT code, video_id, downloads FROM movies")
  else:
    c.execute("SELECT code, video_id, downloads FROM movies WHERE is_vip = 0")
  movies = c.fetchall()
  conn.close()
  if not movies:
    bot.send_message(message.chat.id, "❌ Kinolar topilmadi.")
    return
  code, video_id, downloads = random.choice(movies)
  conn = get_db()
  c = conn.cursor()
  c.execute("UPDATE movies SET downloads = downloads + 1 WHERE code = ?", (code,))
  conn.commit()
  conn.close()

  markup = types.InlineKeyboardMarkup()
  markup.row(
      types.InlineKeyboardButton(
          "📢 Reklama",
          url=f"https://t.me/{get_setting('ad_username').replace('@', '')}",
      ),
      types.InlineKeyboardButton(
          "💎 VIP", callback_data="btn_vip_menu"
      ),
  )
  bot.send_video(
      message.chat.id,
      video_id,
      caption=(
          f"🎬 Kod: `{code}`\n\n{get_setting('ad_text')}\n\n⬇️ Yuklangan:"
          f" {downloads + 1}"
      ),
      parse_mode="Markdown",
      reply_markup=markup,
  )


@bot.message_handler(func=lambda m: m.text == "🔍 Qidirish")
def search(m):
  bot.send_message(m.chat.id, "🔎 Kino kodini yuboring (masalan: `1`):")


def send_movie_by_code(chat_id, user_id, code):
  conn = get_db()
  c = conn.cursor()
  c.execute(
      "SELECT video_id, is_vip, downloads FROM movies WHERE code = ?", (code,)
  )
  movie = c.fetchone()
  conn.close()
  if not movie:
    bot.send_message(chat_id, f"❌ `{code}` kodi topilmadi.", parse_mode="Markdown")
    return
  video_id, is_vip, downloads = movie
  if is_vip == 1 and not is_user_vip(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "💎 VIP sotib olish", callback_data="btn_vip_menu"
        )
    )
    bot.send_message(
        chat_id, "💎 Bu kino faqat VIP foydalanuvchilar uchun!", reply_markup=markup
    )
    return
  conn = get_db()
  c = conn.cursor()
  c.execute("UPDATE movies SET downloads = downloads + 1 WHERE code = ?", (code,))
  conn.commit()
  conn.close()

  markup = types.InlineKeyboardMarkup()
  markup.row(
      types.InlineKeyboardButton(
          "📢 Reklama",
          url=f"https://t.me/{get_setting('ad_username').replace('@', '')}",
      ),
      types.InlineKeyboardButton(
          "💎 VIP", callback_data="btn_vip_menu"
      ),
  )
  bot.send_video(
      chat_id,
      video_id,
      caption=(
          f"🎬 Kod: `{code}`\n\n{get_setting('ad_text')}\n\n⬇️ Yuklangan:"
          f" {downloads + 1}"
      ),
      parse_mode="Markdown",
      reply_markup=markup,
  )


if __name__ == "__main__":
  bot.infinity_polling()
  
