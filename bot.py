from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import BadRequest

from config import BOT_TOKEN, CHANNEL_USERNAME, LIMIT_MINUTES
from db import can_get_config
from config_loader import get_random_config

async def is_member(context, user_id):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )
        return member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ربات کانفیگ زنده\n\n"
        "دستور دریافت:\n"
        "/getconfig"
    )

async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_member(context, user_id):
        await update.message.reply_text(
            "❌ ابتدا عضو کانال شوید:\n"
            f"{CHANNEL_USERNAME}"
        )
        return

    if not can_get_config(user_id, LIMIT_MINUTES):
        await update.message.reply_text(
            "⏳ هر ۱۰ دقیقه فقط یک کانفیگ"
        )
        return

    config = get_random_config()
    if not config:
        await update.message.reply_text("❌ کانفیگی موجود نیست")
        return

    await update.message.reply_text(
        f"✅ کانفیگ شما:\n\n`{config}`",
        parse_mode="Markdown"
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("getconfig", get_config))

app.run_polling()
