from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📡 دریافت کانفیگ", callback_data="get_config")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back")]
    ])
