import random
from telebot import types
from modules.db.models import Word, TranslatedWord, UserWordSetting
from modules.tg_bot.bot_config import CHATBOT_MESSAGE, CHATBOT_BTNS, SESSION
from modules.tg_bot.db_operations import (get_user_id, check_user_in_db, add_new_user, inform_user_of_word_change)
from modules.tg_bot.menu import show_word_variant_menu, show_interaction_menu
from modules.tg_bot.quiz_handling.quiz_handler import validate_and_feedback_user_answer
from modules.tg_bot.word_management import handle_add_word_request, handle_delete_word_request
from modules.tg_bot.bot_init import bot


@bot.message_handler(commands=['start'])
def start_message(message: types.Message) -> None:
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['start_message'])
    show_interaction_menu(message, CHATBOT_BTNS, ['test_knowledge', 'add_word', 'delete_word'])

    # Check if the user is already in the database
    with SESSION as session:
        handle_new_user(session, message)


def handle_new_user(session: SESSION, message: types.Message) -> None:
    """Handles a new user by checking if they already exist in the database. If they don't, the system adds them."""
    try:
        with session.begin():
            check_user_in_db(session, message) or add_new_user(session, message)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call: types.CallbackQuery) -> None:
    """Handles the callback query from the bot."""
    if call.data in ('test_knowledge', 'next'):
        handle_quiz(call.message)
    elif call.data == 'add_word':
        handle_add_word(call.message)
    elif call.data == 'delete_word':
        handle_delete_word(call.message)


@bot.message_handler(commands=['test_knowledge', 'next'])
def handle_quiz(message: types.Message) -> None:
    session = SESSION
    user_id = get_user_id(session, message)
    words = session.query(Word).all()
    visible_words = [word for word in words if not session.query(UserWordSetting).filter_by(
        user_id=user_id, word_id=word.id, is_hidden=True
    ).first()]

    if not visible_words:
        inform_user_of_word_change(message, 'learn_all_words')
        return

    word = random.choice(visible_words)
    user_word_setting = session.query(UserWordSetting).filter_by(
        user_id=user_id, word_id=word.id
    ).first()

    if user_word_setting is None:
        user_word_setting = UserWordSetting(
            user_id=user_id, word_id=word.id, correct_answers=0, is_hidden=False
        )
        session.add(user_word_setting)
        session.commit()

    translations = session.query(TranslatedWord).filter_by(word_id=word.id).all()
    markup, word_id = show_word_variant_menu(words, word)

    if translations:
        russian_word = translations[0].translation
        bot.send_message(
            message.chat.id,
            f'Выбери перевод слова:\n🇷🇺 {russian_word}',
            reply_markup=markup
        )
    else:
        # Handling the case when there are no transfers
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['not_found_translated_word'])

    bot.register_next_step_handler(
        message, validate_and_feedback_user_answer,
        user_word_setting, word, translations
    )


@bot.message_handler(commands=['add_word'])
def handle_add_word(message: types.Message) -> None:
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['add_user_word'])
    bot.register_next_step_handler(message, handle_add_word_request)


@bot.message_handler(commands=['delete_word'])
def handle_delete_word(message: types.Message) -> None:
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['delete_user_word'])
    bot.register_next_step_handler(message, handle_delete_word_request)


def start_bot() -> None:
    """
    Starts the bot's polling process. This function initiates the bot's main loop,
    where it continuously checks for updates and responds to user interactions.
    """
    bot.polling()
