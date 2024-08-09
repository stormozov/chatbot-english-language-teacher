# Initialize bot
import telebot
from modules.tg_bot.bot_config import TG_TOKEN

bot = telebot.TeleBot(TG_TOKEN)
