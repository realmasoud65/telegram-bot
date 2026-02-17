from telegram.ext import ApplicationBuilder
from config import BOT_TOKEN
from handlers.start import start_handler
from handlers.menu import menu_handler
from handlers.get_config import get_config_handler

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(start_handler)
app.add_handler(menu_handler)
app.add_handler(get_config_handler)

app.run_polling()
