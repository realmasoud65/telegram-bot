# -*- coding: utf-8 -*-
import sqlite3
import re
import random
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8301017257:AAEPSFuqaMG5C3aY5vChs-17wuSzMyb9bA8"
CHANNEL_USERNAME = "@xoox_vpn"

# ---------- دیتابیس ----------
db = sqlite3.connect("configs.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config TEXT UNIQUE,
    votes_up INTEGER DEFAULT 0,
    votes_down INTEGER DEFAULT 0
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS votes (
    user_id INTEGER,
    config_id INTEGER,
    vote INTEGER,
    UNIQUE(user_id, config_id)
)
""")
db.commit()

# ---------- کیبورد ثابت ----------
keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("➕ ارسال کانفیگ")],
        [KeyboardButton("📥 دریافت کانفیگ")],
        [KeyboardButton("🔙 بازگشت")]
    ],
    resize_keyboard=False
)

# ---------- تشخیص کانفیگ ----------
def is_valid_config(text):
    return bool(re.match(r'^(vmess|vless|trojan|ss)://', text.strip()))

# ---------- بررسی عضویت ----------
async def check_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "creator", "administrator"]:
            return True
        else:
            await update.message.reply_text(
                f"⚠️ لطفاً ابتدا عضو کانال {CHANNEL_USERNAME} شوید تا از خدمات ربات استفاده کنید."
            )
            return False
    except:
        await update.message.reply_text(
            f"⚠️ لطفاً ابتدا عضو کانال {CHANNEL_USERNAME} شوید تا از خدمات ربات استفاده کنید."
        )
        return False

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        return
    await update.message.delete()
    welcome_text = (
        "🌟 سلام و وقت بخیر!\n\n"
        "🎓 به ربات مدیریت کانفیگ خوش آمدید.\n"
        "💡 این ربات به شما امکان می‌دهد کانفیگ‌های رایگان و امن VPN را دریافت و ارسال کنید.\n"
        "🌐 اینترنت آزاد و کاملاً رایگان است!\n\n"
        "📌 لطفاً از دکمه‌های زیر استفاده کنید:"
    )
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

# ---------- حذف کانفیگ با رأی منفی بالا ----------
def delete_negative_configs():
    cur.execute("SELECT id FROM configs WHERE votes_down >= 5")
    rows = cur.fetchall()
    for (cfg_id,) in rows:
        cur.execute("DELETE FROM configs WHERE id = ?", (cfg_id,))
        cur.execute("DELETE FROM votes WHERE config_id = ?", (cfg_id,))
    db.commit()

# ---------- پیام‌ها ----------
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        return

    text = update.message.text.strip()
    user_id = update.message.from_user.id
    await update.message.delete()

    if text == "🔙 بازگشت":
        await update.message.reply_text(
            "🔹 به منوی اصلی بازگشتید. لطفاً گزینه مورد نظر خود را انتخاب کنید:",
            reply_markup=keyboard
        )
        return

    if text == "➕ ارسال کانفیگ":
        await update.message.reply_text(
            "📥 لطفاً کانفیگ معتبر خود را ارسال نمایید.\n"
            "🎯 فرمت‌های معتبر: vmess:// | vless:// | trojan:// | ss://"
        )
        return

    if text.startswith("📥 دریافت کانفیگ"):
        parts = text.split()
        n = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1

        # فقط کانفیگ‌هایی که کاربر قبلاً دریافت نکرده
        cur.execute("""
            SELECT id, config FROM configs
            WHERE id NOT IN (
                SELECT config_id FROM votes WHERE user_id = ?
            )
        """, (user_id,))
        rows = cur.fetchall()

        if not rows:
            await update.message.reply_text(
                "ℹ️ شما تاکنون همه کانفیگ‌های موجود را دریافت کرده‌اید. لطفاً بعداً مراجعه کنید."
            )
            return

        selected = random.sample(rows, min(n, len(rows)))
        for cfg_id, cfg in selected:
            try:
                cur.execute(
                    "INSERT INTO votes (user_id, config_id, vote) VALUES (?,?,?)",
                    (user_id, cfg_id, 1)
                )
                cur.execute(
                    "UPDATE configs SET votes_up = votes_up + 1 WHERE id = ?",
                    (cfg_id,)
                )
                db.commit()
                await update.message.reply_text(
                    f"✅ کانفیگ دریافت شد:\n\n{cfg}\n\n👍 رأی شما ثبت شد."
                )
            except sqlite3.IntegrityError:
                pass
        return

    # ---------- ثبت کانفیگ ----------
    if is_valid_config(text):
        try:
            cur.execute("INSERT INTO configs (config) VALUES (?)", (text,))
            db.commit()
            await update.message.reply_text(
                "🎉 کانفیگ شما با موفقیت ثبت شد. سپاس از همکاری شما!"
            )
        except sqlite3.IntegrityError:
            await update.message.reply_text(
                "⚠️ این کانفیگ قبلاً ثبت شده است. لطفاً کانفیگ دیگری ارسال نمایید."
            )
    else:
        await update.message.reply_text(
            "❌ فرمت ارسال شده معتبر نیست. لطفاً کانفیگ خود را مطابق فرمت‌های مجاز ارسال نمایید."
        )

    delete_negative_configs()

# ---------- اجرا ----------
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))

print("Bot is running...")
app.run_polling()