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
CHATBOT_MESSAGE = CHATBOT_DATA['messages']
CHATBOT_BTNS = CHATBOT_DATA['buttons']

# Initialize bot
bot = telebot.TeleBot(TG_TOKEN)

cards = {
    'hello': 'привет',
    'goodbye': 'прощай',
    'thank you': 'спасибо',
    'card': 'карта',
    'dictionary': 'словарь',
    'computer': 'компьютер',
    'keyboard': 'клавиатура',
    'mouse': 'мышь',
    'book': 'книга',
    'pen': 'ручка',
    'pencil': 'карандаш',
    'laptop': 'ноутбук',
    'printer': 'принтер',
    'monitor': 'монитор',
}


@bot.message_handler(commands=['start'])
def start_message(message):
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['start_message'])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton(CHATBOT_BTNS['test_knowledge'])
    markup.add(item1)
    bot.send_message(message.chat.id, 'Нажми на кнопку ниже 👇, чтобы начать!', reply_markup=markup)


# Обработка кнопок
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == CHATBOT_BTNS['test_knowledge'] or message.text == CHATBOT_BTNS['next']:
        card = random.choice(list(cards.keys()))
        variants = [card] + random.sample([key for key in cards.keys() if key != card], 3)
        random.shuffle(variants)
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

        row = []
        for variant in variants:
            item = types.KeyboardButton(variant)
            row.append(item)
            if len(row) == 2:
                markup.row(*row)
                row = []

        if row:
            markup.row(*row)

        bot.send_message(message.chat.id, f'Выбери перевод слова:\n🇷🇺 {cards[card]}', reply_markup=markup)
        bot.register_next_step_handler(message, check_answer, card)
    else:
        bot.send_message(message.chat.id, 'Нажмите на кнопку "Проверить знания"')


# Проверка ответа
def check_answer(message, card):
    if message.text == card:
        bot.send_message(message.chat.id, '✅')
        bot.send_message(message.chat.id, f'Правильно!\nСлово 🇷🇺 {cards[card]} переводится как 🇺🇸 {card}')
    else:
        bot.send_message(message.chat.id, '❌')
        bot.send_message(message.chat.id, f'Неправильно.\nПравильный ответ: {card}')

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton(CHATBOT_BTNS['next'])
    item2 = types.KeyboardButton(CHATBOT_BTNS['add_word'])
    item3 = types.KeyboardButton(CHATBOT_BTNS['delete_word'])

    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def start_bot():
    """ Start telegrambot """
    bot.polling()
