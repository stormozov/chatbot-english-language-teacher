import random
import telebot
from telebot import types
from modules.config.read_config import read_config
from modules.db.db_session import create_db_session
from modules.db.models import Word, TranslatedWord, UserWordSetting, User
from modules.fs_tools.path_utils import get_absolute_path
from modules.read_file.read_file import read_file

path_to_config: str = get_absolute_path(['settings.ini'])
path_to_json: str = get_absolute_path(['data', 'chatbot.json'])

TG_TOKEN = read_config(path_to_config, 'TG')['token']
DB = read_config(path_to_config, 'DB')
CHATBOT_DATA = read_file(path_to_json)
CHATBOT_MESSAGE = CHATBOT_DATA['messages']
CHATBOT_BTNS = CHATBOT_DATA['buttons']

# Initialize bot
bot = telebot.TeleBot(TG_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['start_message'])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton(CHATBOT_BTNS['test_knowledge'])
    markup.add(item1)
    bot.send_message(message.chat.id, 'Нажми на кнопку ниже 👇, чтобы начать!', reply_markup=markup)

    # Check if the user is already in the database
    session = create_db_session(DB)[0]
    user = session.query(User).filter_by(tg_id=message.from_user.id).first()

    if not user:
        # If the user is not in the database, add them
        new_user = User(tg_id=message.from_user.id, username=message.from_user.username)
        session.add(new_user)
        session.commit()

    session.close()


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """
        A function that handles text messages from the user.
        It generates answer choices for a quiz based on the user's text input.
    """
    if message.text == CHATBOT_BTNS['test_knowledge'] or message.text == CHATBOT_BTNS['next']:
        session = create_db_session(DB)[0]
        words = session.query(Word).all()
        word = random.choice(words)
        translations = session.query(TranslatedWord).filter_by(word_id=word.id).all()
        session.close()

        # Create a list of answer choices
        variants = [word.word]  # Английское слово
        # Add 3 random English words as distractors
        distractors = [w.word for w in words if w.word != word.word]
        random.shuffle(distractors)
        variants.extend(distractors[:3])
        random.shuffle(variants)
        word_id = word.id
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

        if translations:
            russian_word = translations[0].translation
            bot.send_message(
                message.chat.id,
                f'Выбери перевод слова:\n🇷🇺 {russian_word}',
                reply_markup=markup
            )
        else:
            # Handling the case when there are no transfers
            bot.send_message(message.chat.id, 'Нет перевода для этого слова')

        bot.register_next_step_handler(message, check_answer, word_id)

    if message.text == CHATBOT_BTNS['add_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['add_user_word'])
        bot.register_next_step_handler(message, add_word)
    elif message.text == CHATBOT_BTNS['delete_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['delete_user_word'])
        bot.register_next_step_handler(message, delete_word)


def check_answer(message, card):
    """
        Check the user's answer against the correct word and send a response message.

        Parameters:
            message (telegram.Message): The message object containing the user's answer.
            card (int): The ID of the word card.
    """
    session = create_db_session(DB)[0]
    word = session.query(Word).get(card)
    translations = session.query(TranslatedWord).filter_by(word_id=word.id).all()
    session.close()

    correct_word = word.word

    if message.text == correct_word:
        bot.send_message(message.chat.id, '✅')
        bot.send_message(
            message.chat.id,
            f'Правильно!\nСлово 🇷🇺 {correct_word} переводится как 🇺🇸 {translations[0].translation}'
        )
    else:
        bot.send_message(message.chat.id, '❌')
        bot.send_message(
            message.chat.id,
            f'Неправильно.\nПравильный ответ: {correct_word}'
        )

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton(CHATBOT_BTNS['next'])
    item2 = types.KeyboardButton(CHATBOT_BTNS['add_word'])
    item3 = types.KeyboardButton(CHATBOT_BTNS['delete_word'])

    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def add_word(message):
    """Add a word to the database with the corresponding translation and user settings."""
    session = create_db_session(DB)[0]
    user_id = session.query(User).filter_by(tg_id=message.from_user.id).first().id
    word, translation = message.text.split(', ')
    word_obj = session.query(Word).filter_by(word=word, user_id=user_id).first()

    if not word_obj:
        word_obj = Word(word=word, user_id=user_id)
        session.add(word_obj)
        session.commit()

    translated_word_obj = session.query(TranslatedWord).filter_by(word_id=word_obj.id, translation=translation).first()
    if not translated_word_obj:
        translated_word_obj = TranslatedWord(word_id=word_obj.id, translation=translation)
        session.add(translated_word_obj)
        session.commit()

    user_word_setting_obj = session.query(UserWordSetting).filter_by(user_id=user_id, word_id=word_obj.id).first()
    if not user_word_setting_obj:
        user_word_setting_obj = UserWordSetting(user_id=user_id, word_id=word_obj.id)
        session.add(user_word_setting_obj)
        session.commit()

    session.close()

    bot.send_message(message.chat.id, f'Слово {word} и его перевод {translation} добавлены ✅ успешно!')

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton(CHATBOT_BTNS['next'])
    item2 = types.KeyboardButton(CHATBOT_BTNS['add_word'])
    item3 = types.KeyboardButton(CHATBOT_BTNS['delete_word'])
    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def start_bot():
    """ Start telegrambot """
    bot.polling()
