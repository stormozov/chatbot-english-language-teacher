import random
from typing import Union
import telebot
from telebot import types
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
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


def get_user_id(session, message: types.Message) -> int:
    """Get the user ID from the database"""
    return session.query(User).filter_by(tg_id=message.from_user.id).first().id


@bot.message_handler(commands=['start'])
def start_message(message: types.Message) -> None:
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['start_message'])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton(CHATBOT_BTNS['test_knowledge'])
    markup.add(item1)
    bot.send_message(message.chat.id, 'Нажми на кнопку ниже 👇, чтобы начать!', reply_markup=markup)

    # Check if the user is already in the database
    session = create_db_session(DB)[0]
    user = get_user_id(session, message)

    if not user:
        # If the user is not in the database, add them
        new_user = User(tg_id=message.from_user.id, username=message.from_user.username)
        session.add(new_user)
        session.commit()

    session.close()


@bot.message_handler(content_types=['text'])
def handle_quiz_or_word_management(message: types.Message) -> None:
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

        bot.register_next_step_handler(message, validate_and_feedback_user_answer, word_id)

    if message.text == CHATBOT_BTNS['add_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['add_user_word'])
        bot.register_next_step_handler(message, handle_add_word_request)
    elif message.text == CHATBOT_BTNS['delete_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['delete_user_word'])
        bot.register_next_step_handler(message, handle_delete_word_request)


def show_interaction_menu(bot: telebot.TeleBot, message: types.Message) -> None:
    """Send the main menu"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(CHATBOT_BTNS[btn]) for btn in ['next', 'add_word', 'delete_word']])
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def validate_and_feedback_user_answer(message: types.Message, card: int) -> None:
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

    show_interaction_menu(bot, message)


def get_word_obj(session, word: str, user_id: int) -> Union[Word, None]:
    """Get the word object from the database"""
    return session.query(Word).filter(func.lower(Word.word) == func.lower(word), Word.user_id == user_id).first()


def add_word_to_db(session, word: str, user_id: int, translation: str, message: types.Message) -> None:
    """Add a word to the database"""
    try:
        word_obj = Word(word=word, user_id=user_id)
        translated_word_obj = TranslatedWord(word=word_obj, translation=translation)
        user_word_setting_obj = UserWordSetting(user_id=user_id, word=word_obj)

        session.add_all([word_obj, translated_word_obj, user_word_setting_obj])
        session.commit()  # Commit the transaction
    except IntegrityError as e:
        session.rollback()  # Rollback the transaction on error
        bot.send_message(message.chat.id, f'Слово {word} уже добавлено в вашем словаре.')


def delete_word_from_db(session, word_obj: Word) -> None:
    """Delete a word from the database"""
    translated_words = session.query(TranslatedWord).filter_by(word_id=word_obj.id).all()
    user_word_setting_obj = session.query(UserWordSetting).filter_by(word_id=word_obj.id).first()

    for translated_word in translated_words:
        session.delete(translated_word)

    if user_word_setting_obj:
        session.delete(user_word_setting_obj)

    session.delete(word_obj)
    session.commit()


def inform_user_of_word_change(bot: telebot.TeleBot, message: types.Message, word: str, action: str) -> None:
    """Inform the user of the change in the dictionary"""
    if action == 'add':
        bot.send_message(message.chat.id, f'Слово {word} и его перевод добавлены успешно!')
    elif action == 'delete':
        bot.send_message(message.chat.id, f'Слово {word} и его переводы удалены успешно!')


def handle_add_word_request(message: types.Message) -> None:
    """Handles the request to add a new word to the user's word list."""
    session = create_db_session(DB)[0]
    user_id = get_user_id(session, message)
    word, translation = message.text.split(', ')
    word_obj = get_word_obj(session, word, user_id)

    if not word_obj:
        add_word_to_db(
            session, word, user_id,
            translation, message
        )
        inform_user_of_word_change(bot, message, word, 'add')

    session.close()
    show_interaction_menu(bot, message)


def handle_delete_word_request(message: types.Message) -> None:
    """Handles the request to delete a word from the user's word list."""
    session = create_db_session(DB)[0]
    user_id = get_user_id(session, message)
    word = message.text
    word_obj = get_word_obj(session, word, user_id)

    if word_obj:
        delete_word_from_db(session, word_obj)
        inform_user_of_word_change(bot, message, word, 'delete')
    else:
        bot.send_message(message.chat.id, f'Слово {word} не найдено в вашем словаре.')

    session.close()
    show_interaction_menu(bot, message)


def start_bot() -> None:
    """
    Starts the bot's polling process. This function initiates the bot's main loop, where it continuously checks for
    updates and responds to user interactions.
    """
    bot.polling()
