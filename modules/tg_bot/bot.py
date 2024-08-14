import random
from telebot import types
from modules.db.models import Word, TranslatedWord, UserWordSetting
from modules.tg_bot.bot_config import CHATBOT_MESSAGE, CHATBOT_BTNS, SESSION
from modules.tg_bot.db_operations import (get_user_id, check_user_in_db, add_new_user, inform_user_of_word_change)
from modules.tg_bot.menu import show_word_variant_menu, show_one_item_menu
from modules.tg_bot.quiz_handling.quiz_handler import validate_and_feedback_user_answer
from modules.tg_bot.word_management import handle_add_word_request, handle_delete_word_request
from modules.tg_bot.bot_init import bot


@bot.message_handler(commands=['start'])
def start_message(message: types.Message) -> None:
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['start_message'])
    show_one_item_menu(
        message, CHATBOT_BTNS['test_knowledge'],
        CHATBOT_MESSAGE['second_message']
    )

    # Check if the user is already in the database
    with SESSION as session:
        handle_new_user(session, message)


def handle_new_user(session, message):
    if not check_user_in_db(session, message):
        add_new_user(session, message)


@bot.message_handler(content_types=['text'])
def handle_quiz_or_word_management(message: types.Message) -> None:
    """
    Handles the quiz or word management functionality of the chatbot.

    This function is triggered when the user sends a text message to the chatbot.
    It checks the message text and performs the corresponding action:
    - If the message text is 'test_knowledge' or 'next', it selects a random word from the database,
      generates a menu with word variants, and sends it to the user.
    - If the message text is 'add_word', it sends a message to the user to add a new word.
    - If the message text is 'delete_word', it sends a message to the user to delete a word.

    Parameters:
        message (types.Message): The message object containing the user's input.

    Returns:
        None
    """
    if message.text == CHATBOT_BTNS['test_knowledge'] or message.text == CHATBOT_BTNS['next']:
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

    if message.text == CHATBOT_BTNS['add_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['add_user_word'])
        bot.register_next_step_handler(message, handle_add_word_request)
    elif message.text == CHATBOT_BTNS['delete_word']:
        bot.send_message(message.chat.id, CHATBOT_MESSAGE['delete_user_word'])
        bot.register_next_step_handler(message, handle_delete_word_request)


def start_bot() -> None:
    """
    Starts the bot's polling process. This function initiates the bot's main loop,
    where it continuously checks for updates and responds to user interactions.
    """
    bot.polling()
