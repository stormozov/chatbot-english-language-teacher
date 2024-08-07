import random
import telebot
from telebot import types
from modules.config.read_config import read_config
from modules.fs_tools.path_utils import get_absolute_path
from modules.read_file.read_file import read_file

path_to_config: str = get_absolute_path(['settings.ini'])
path_to_json: str = get_absolute_path(['data', 'chatbot.json'])

TG_TOKEN = read_config(path_to_config, 'TG')['token']
CHATBOT_DATA = read_file(path_to_json)

# Initialize bot
bot = telebot.TeleBot(TG_TOKEN)

cards = {
    'hello': 'привет',
    'goodbye': 'прощай',
    'thank you': 'спасибо',
    # Добавьте больше карточек сюда
}


@bot.message_handler(commands=['start'])
def start_message(message):
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_DATA['start_message'])
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton('Проверить знания')
    markup.add(item1)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


# Обработка кнопок
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == 'Проверить знания':
        card = random.choice(list(cards.keys()))
        bot.send_message(message.chat.id, f'Английское слово: {card}\nВведите перевод:')
        bot.register_next_step_handler(message, check_answer, card)


# Проверка ответа
def check_answer(message, card):
    if message.text.lower() == cards[card].lower():
        bot.send_message(message.chat.id, 'Правильно!')
    else:
        bot.send_message(message.chat.id, f'Неправильно. Правильный ответ: {cards[card]}')


def start_bot():
    """ Start telegrambot """
    bot.polling()
