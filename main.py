from datetime import datetime, timedelta
import random
import sqlite3
import telebot
from telebot import types

TOKEN = "8816940858:AAEwDQ94ues00rcG1RVkNMPumQh7Xxgfowc"
ADMIN_ID = 8753350906
BOT_USERNAME = "Kinolarqbot"

bot = telebot.TeleBot(TOKEN)
user_states = {}

# --- BAZA YO'LI VA SOZLAMALAR ---
DB_NAME = "bot_database.db"


def init_db():
  conn = sqlite3.connect(DB_NAME, check_same_thread=False)
  cursor = conn.cursor()
  cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            joined_date TEXT,
            is_vip INTEGER DEFAULT 0,
            vip_expire_date TEXT,
            is_banned INTEGER DEFAULT 0
        )
    """
  )
  cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS movies (
            code TEXT PRIMARY KEY,
            video_id TEXT,
            is_vip INTEGER DEFAULT 0,
            downloads INTEGER DEFAULT 0
        )
    """
  )
  cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS channels (
            channel_username TEXT PRIMARY KEY
        )
    """
  )
  cursor.execute(
      """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """
  )
  conn.commit()

  # Standart reklama va matnlar
  cursor.execute(
      "INSERT OR IGNORE INTO settings (key, value) VALUES ('ad_username',"
      " '@reklamuchun1')"
  )
  conn.commit()

  cursor.execute(
      """
    INSERT OR IGNORE INTO settings (key, value) 
    VALUES ('ad_text', '🔥 **ZAYAFKA KANALLARGA ZAKAZ OLAMAN!**\n\nKanalga odam kerakmi? Unda yozing ↘️👇 Jivoy, aktiv auditoriya\n⚡️ Tez va sifatli ishlaymiz\n📈 Narxlar hamyonbop\n📊 Kanalni tezroq o''stirishga yordam beramiz\n\n1000 ta zayafka - kelishilgan narxda ✅\nKo''p miqdorga alohida skidka bor 💥\n\n👉 Zakaz uchun lichkaga yozing')
    """
  )
  conn.commit()

  cursor.execute("SELECT COUNT(*) FROM channels")
  if cursor.fetchone()[0] == 0:
    default_channels = ["@max_films01", "@reklamuchun1", "@sevshgnrlr"]
    for ch in default_channels:
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
  current_channels = get_current_channels()
  for ch in current_channels:
    try:
      status = bot.get_chat_member(ch, user_id).status
      if status not in ["member", "administrator", "creator"]:
        return False
    except Exception as e:
      print(f"Obunani tekshirishda xatolik ({ch}): {e}")
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
  if is_vip == 1:
    if expire_date_str:
      expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d %H:%M:%S")
      if datetime.now() > expire_date:
        remove_vip_status(user_id)
        return False
    return True
  return False


def remove_vip_status(user_id):
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute(
      "UPDATE users SET is_vip = 0, vip_expire_date = NULL WHERE user_id = ?",
      (user_id,),
  )
  conn.commit()
  conn.close()


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
  username = message.from_user.username
  current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  conn = get_db()
  cursor = conn.cursor()
  cursor.execute(
      "INSERT OR IGNORE INTO users (user_id, username, joined_date) VALUES (?,"
      " ?, ?)",
      (user_id, username, current_date),
  )
  conn.commit()
  conn.close()

  if is_user_banned(user_id):
    bot.send_message(message.chat.id, "❌ Siz botdan bloklangansiz!")
    return

  if not is_user_vip(user_id) and not check_sub(user_id):
    markup = types.InlineKeyboardMarkup()
    current_channels = get_current_channels()
    for ch in current_channels:
      ch_clean = ch.replace("@", "").replace("https://t.me/", "")
      markup.add(
          types.InlineKeyboardButton(
              "📢 Kanalga o'tish", url=f"https://t.me/{ch_clean}"
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
        "✨ Botdan foydalanish uchun quyidagi barcha kanallarga obuna bo'ling:",
        reply_markup=markup,
    )
    return

  text = message.text or ""
  if text.startswith("/start kino_"):
    code = text.split("_")[1]
    send_movie_by_code(message.chat.id, user_id, code)
    return

  show_main_menu(message.chat.id, user_id)


@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def callback_sub(call):
  user_id = call.from_user.id
  if check_sub(user_id):
    bot.answer_callback_query(call.id, "Rahmat! Obuna tasdiqlandi ✅")
    try:
      bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
      pass
    show_main_menu(call.message.chat.id, user_id)
  else:
    bot.answer_callback_query(
        call.id,
        "Siz hali hamma kanallarga a'zo bo'lmadingiz! ❌",
        show_alert=True,
    )


# --- ADMIN BOSHQARUVLARI ---
@bot.message_handler(
    func=lambda message: message.text == "📊 Statistika"
    and message.from_user.id == ADMIN_ID
)
def admin_stats_panel(message):
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute("SELECT COUNT(*) FROM users")
  total_users = cursor.fetchone()[0]
  cursor.execute("SELECT COUNT(*) FROM movies")
  total_movies = cursor.fetchone()[0]
  cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
  total_vips = cursor.fetchone()[0]
  cursor.execute("SELECT SUM(downloads) FROM movies")
  total_downloads = cursor.fetchone()[0] or 0
  conn.close()

  stats_text = (
      f"📊 **Botning To'liq Statistikasi:**\n\n👥 Jami foydalanuvchilar:"
      f" <b>{total_users}</b> ta\n💎 VIP obunachilar: <b>{total_vips}</b>"
      f" ta\n🎬 Bazadagi jami kinolar: <b>{total_movies}</b> ta\n📥 Jami"
      f" ko'rilgan/yuklangan kinolar: <b>{total_downloads}</b> marta\n🟢 Bot"
      " holati: <b>Ishlayapti (24/7)</b>"
  )
  bot.reply_to(message, stats_text, parse_mode="HTML")


@bot.message_handler(
    func=lambda message: message.text == "🤖 Bot holati"
    and message.from_user.id == ADMIN_ID
)
def admin_bot_status(message):
  bot.reply_to(
      message,
      "🟢 Bot holati: **Aktiv (24/7 ishlayapti)**\n⚡ Himoya: Yoqilgan"
      " (`protect_content` faol)\n🗄 Ma'lumotlar bazasi: SQLite",
      parse_mode="Markdown",
  )


@bot.message_handler(
    func=lambda message: message.text == "📢 Kanallarni sozlash"
    and message.from_user.id == ADMIN_ID
)
def admin_channels_config(message):
  current_channels = get_current_channels()
  channels_str = (
      "\n".join(current_channels) if current_channels else "Hozircha kanallar yo'q."
  )
  bot.reply_to(
      message,
      f"📢 **Hozirgi majburiy obuna kanallari:**\n{channels_str}",
      parse_mode="Markdown",
  )


@bot.message_handler(
    func=lambda message: message.text == "➕ Kanal qo'shish"
    and message.from_user.id == ADMIN_ID
)
def admin_add_channel_start(message):
  user_states[message.from_user.id] = "waiting_for_new_channel"
  bot.reply_to(
      message,
      "➕ Yangi kanal username'ini yuboring (Masalan: `@kanal_nomi`):",
  )


@bot.message_handler(
    func=lambda message: message.text == "🗑 Kanalni o'chirish"
    and message.from_user.id == ADMIN_ID
)
def admin_remove_channel_start(message):
  current_channels = get_current_channels()
  if not current_channels:
    bot.reply_to(message, "❌ Hozircha majburiy obunada kanallar mavjud emas.")
    return

  markup = types.InlineKeyboardMarkup()
  for ch in current_channels:
    markup.add(
        types.InlineKeyboardButton(
            f"❌ O'chirish: {ch}", callback_data=f"del_ch_{ch}"
        )
    )

  bot.reply_to(
      message,
      "🗑 O'chirmoqchi bo'lgan kanalingizni tanlang:",
      reply_markup=markup,
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith("del_ch_"))
def callback_delete_channel(call):
  if call.from_user.id != ADMIN_ID:
    return
  channel_name = call.data.replace("del_ch_", "")
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute("DELETE FROM channels WHERE channel_username = ?", (channel_name,))
  conn.commit()
  conn.close()
  bot.answer_callback_query(call.id, f"{channel_name} o'chirildi!")
  try:
    bot.edit_message_text(
        f"✅ <b>{channel_name}</b> o'chirildi!",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="HTML",
    )
  except:
    pass


@bot.message_handler(
    func=lambda message: message.text == "⚙️ Reklamani o'zgartirish"
    and message.from_user.id == ADMIN_ID
)
def admin_change_ad_start(message):
  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton(
          "📝 Reklama matnini o'zgartirish", callback_data="set_ad_text"
      )
  )
  markup.add(
      types.InlineKeyboardButton(
          "🔗 Reklama silka/username'ni o'zgartirish", callback_data="set_ad_user"
      )
  )
  current_text = get_setting("ad_text")
  current_user = get_setting("ad_username")
  bot.reply_to(
      message,
      (
          "⚙️ **Hozirgi Reklama Sozlamalari:**\n\n<b>Username:</b>"
          f" {current_user}\n\n<b>Matn:</b>\n{current_text}"
      ),
      parse_mode="HTML",
      reply_markup=markup,
  )


@bot.callback_query_handler(
    func=lambda call: call.data in ["set_ad_text", "set_ad_user"]
)
def callback_set_ad(call):
  if call.from_user.id != ADMIN_ID:
    return
  if call.data == "set_ad_text":
    user_states[call.from_user.id] = "waiting_for_new_ad_text"
    bot.send_message(call.message.chat.id, "✍️ Yangi reklama matnini yuboring:")
  elif call.data == "set_ad_user":
    user_states[call.from_user.id] = "waiting_for_new_ad_user"
    bot.send_message(
        call.message.chat.id,
        "🔗 Yangi reklama username'ini yuboring (Masalan: `@reklamuchun1`):",
    )


@bot.message_handler(
    func=lambda message: message.text == "🗑 Kino o'chirish"
    and message.from_user.id == ADMIN_ID
)
def admin_delete_movie_start(message):
  user_states[message.from_user.id] = "waiting_for_movie_code_to_delete"
  bot.reply_to(message, "🗑 O'chirmoqchi bo'lgan kino **kodini** yuboring:")


@bot.message_handler(
    func=lambda message: message.text == "🚫 VIP'dan chiqarish"
    and message.from_user.id == ADMIN_ID
)
def admin_remove_vip_start(message):
  user_states[message.from_user.id] = "waiting_for_remove_vip_id"
  bot.reply_to(
      message,
      "👤 VIP statusini olib tashlamoqchi bo'lgan foydalanuvchining **Telegram"
      " ID** raqamini yuboring:",
  )


@bot.message_handler(
    func=lambda message: message.text == "📢 Xabar yuborish (Reklama)"
    and message.from_user.id == ADMIN_ID
)
def admin_start_broadcast(message):
  user_states[message.from_user.id] = "waiting_for_broadcast_text"
  bot.reply_to(
      message,
      "📢 Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring:",
  )


@bot.message_handler(
    func=lambda message: message.text == "🎬 Kino yuklash"
    and message.from_user.id == ADMIN_ID
)
def admin_movie_upload_menu(message):
  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton(
          "🎬 Oddiy video qo'shish", callback_data="add_type_0"
      )
  )
  markup.add(
      types.InlineKeyboardButton(
          "💎 VIP video qo'shish", callback_data="add_type_1"
      )
  )
  bot.send_message(
      message.chat.id, "🔽 Quyidagilardan birini tanlang:", reply_markup=markup
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith("add_type_"))
def callback_add_type(call):
  if call.from_user.id != ADMIN_ID:
    return
  v_type = int(call.data.split("_")[2])
  user_states[call.from_user.id] = {
      "step": "admin_direct_wait_video",
      "type": v_type,
  }
  v_name = "VIP" if v_type == 1 else "Oddiy"
  bot.edit_message_text(
      f"📤 {v_name} videoni yuboring:",
      call.message.chat.id,
      call.message.message_id,
  )


@bot.message_handler(func=lambda message: message.text == "💎 Premium Obuna")
def vip_subscription_menu_msg(message):
  vip_subscription_menu(message)


@bot.callback_query_handler(func=lambda call: call.data == "btn_vip_menu")
def vip_subscription_menu_call(call):
  vip_subscription_menu(call)


def vip_subscription_menu(event):
  chat_id = event.message.chat.id if hasattr(event, "message") else event.chat.id
  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton(
          "1 oylik — 15,000 so'm", callback_data="pay_uz_1"
      )
  )
  markup.add(
      types.InlineKeyboardButton(
          "3 oylik — 20,000 so'm", callback_data="pay_uz_3"
      )
  )
  markup.add(
      types.InlineKeyboardButton(
          "6 oylik — 35,000 so'm", callback_data="pay_uz_6"
      )
  )
  text = "💎 **Premium Obuna**\nTarifni tanlang:"
  bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def vip_payment_details(call):
  data_parts = call.data.split("_")
  period = data_parts[2]
  prices = {"1": "15,000 so'm", "3": "20,000 so'm", "6": "35,000 so'm"}
  price = prices.get(period, "15,000 so'm")
  text = (
      f"💎 **Tarif:** {period} oylik ({price})\n\n💳 **Karta raqam:** `6262 5701"
      " 4806 4381`\n👤 **Karta egasi:** Obidjonova M\n\n📸 Pulni o'tkazgach,"
      " to'lov chekining **skrinshotini** shu botga yuboring. Admin"
      " tasdiqlagach VIP obuna avtomatik ochiladi!"
  )
  user_states[call.from_user.id] = f"waiting_for_check_{period}"
  bot.send_message(call.message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text == "💡 Kino tavsiya qilish")
def recommend_movie(message):
  user_states[message.from_user.id] = "recommending_movie"
  bot.send_message(
      message.chat.id,
      "✍️ Ko'rmoqchi bo'lgan kinosingiz nomini yozib yuboring, adminga"
      " yuboramiz:",
  )


@bot.message_handler(
    func=lambda message: message.text == "📬 Shaxsiy kino qo'shish"
)
def personal_add_movie(message):
  user_states[message.from_user.id] = "personal_add_video"
  bot.send_message(message.chat.id, "📤 Shaxsiy kino videosini yuboring:")


@bot.message_handler(
    func=lambda message: message.text == "🎬 Admin orqali kino qo'shish"
)
def admin_add_movie(message):
  user_states[message.from_user.id] = "admin_add_video"
  bot.send_message(
      message.chat.id, "📤 Adminga yuborish uchun kino videosini yuboring:"
  )


@bot.message_handler(func=lambda message: message.text == "🎲 Tasodifiy")
def random_movie(message):
  conn = get_db()
  cursor = conn.cursor()
  if is_user_vip(message.from_user.id):
    cursor.execute("SELECT code, video_id, is_vip, downloads FROM movies")
  else:
    cursor.execute(
        "SELECT code, video_id, is_vip, downloads FROM movies WHERE is_vip = 0"
    )
  movies = cursor.fetchall()
  conn.close()

  if not movies:
    bot.send_message(message.chat.id, "❌ Hozircha bazada kinolar mavjud emas.")
  else:
    code, video_id, is_vip, downloads = random.choice(movies)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE movies SET downloads = downloads + 1 WHERE code = ?", (code,)
    )
    conn.commit()
    conn.close()
    new_downloads = downloads + 1

    ad_text = get_setting("ad_text")
    ad_user = get_setting("ad_username")

    caption = (
        f"🎬 **Kino kodi:** `{code}`\n\n{ad_text}\n{ad_user}\n\n⬇️ Yuklab olingan:"
        f" {new_downloads} ta"
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            "📢 Reklama / Zakaz",
            url=f"https://t.me/{ad_user.replace('@', '')}",
        ),
        types.InlineKeyboardButton(
            "💎 Premium obuna", callback_data="btn_vip_menu"
        ),
    )

    bot.send_video(
        message.chat.id,
        video_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup,
        protect_content=True,
    )


@bot.message_handler(func=lambda message: message.text == "🔍 Qidirish")
def search_hint(message):
  bot.send_message(
      message.chat.id,
      "🔎 Kino topish uchun kino **kodini** yuboring (masalan: `1`, `120`):",
      parse_mode="Markdown",
  )


@bot.message_handler(func=lambda message: message.text == "📢 Reklama")
def reklama_menu(message):
  ad_user = get_setting("ad_username")
  bot.send_message(
      message.chat.id,
      f"📢 Reklama va xizmatlardan foydalanish uchun murojaat qiling: {ad_user}",
  )


def send_movie_by_code(chat_id, user_id, code):
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute(
      "SELECT video_id, is_vip, downloads FROM movies WHERE code = ?", (code,)
  )
  movie = cursor.fetchone()
  conn.close()

  if movie:
    video_id, is_vip, downloads = movie
    if is_vip == 1 and not is_user_vip(user_id):
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              "💎 Premium Obuna sotib olish", callback_data="btn_vip_menu"
          )
      )
      bot.send_message(
          chat_id,
          "💎 Bu kino faqat **VIP foydalanuvchilar** uchun mo'ljallangan!",
          reply_markup=markup,
          parse_mode="Markdown",
      )
      return

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE movies SET downloads = downloads + 1 WHERE code = ?", (code,)
    )
    conn.commit()
    conn.close()
    new_downloads = downloads + 1

    ad_text = get_setting("ad_text")
    ad_user = get_setting("ad_username")

    caption = (
        f"🎬 **Kino kodi:** `{code}`\n\n{ad_text}\n{ad_user}\n\n⬇️ Yuklab olingan:"
        f" {new_downloads} ta"
    )

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(
            "📢 Reklama / Zakaz"
