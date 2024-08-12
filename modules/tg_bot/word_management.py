import re
from typing import Union
from telebot import types
from modules.tg_bot.bot_init import bot
from modules.tg_bot.bot_config import SESSION, CHATBOT_BTNS, CHATBOT_ERRORS
from modules.tg_bot.db_operations import (get_user_id, get_word_by_user_id, add_word_to_db, delete_word_from_db,
                                          inform_user_of_word_change, remove_word_from_view, word_exists_in_db)
from modules.tg_bot.menu import show_interaction_menu


def validate_user_input(message: types.Message) -> tuple[Union[str, None], Union[str, None]]:
    """Validates user input and returns word and translation"""
    user_input = message.text.split(',', 1)
    if len(user_input) != 2:
        inform_user_of_word_change(message, 'add_word_value')
        return None, None
    return user_input[0].strip().capitalize(), user_input[1].strip().capitalize()


def check_word_format(word: str, translation: str):
    """Checks whether the user's input is a word in the correct format"""
    return re.match(r'^[a-zA-Z]+$', word) and re.match(r'^[а-яА-ЯёЁ]+$', translation)


def handle_add_word_request(message: types.Message) -> None:
    """Handles the request to add a new word to the user's word list."""
    session = SESSION
    user_id = get_user_id(session, message)

    word, translation = validate_user_input(message)

    if not word or not translation:
        return

    if not check_word_format(word, translation):
        inform_user_of_word_change(message, 'add_word_value')
        return

    word_obj = get_word_by_user_id(session, word, user_id)
    session.close()

    if not word_obj:
        add_word_to_db(session, word, user_id, translation, message)
        inform_user_of_word_change(message, 'add', word)

    show_interaction_menu(message, CHATBOT_BTNS, ['next', 'add_word', 'delete_word'])


def handle_word_not_in_user_db(session, user_id, word, message):
    """Handles the case when a word is not in the user's database."""
    is_word = word_exists_in_db(session, word)
    if is_word is None:
        bot.send_message(message.chat.id, CHATBOT_ERRORS['word_not_found'])
        session.close()
        return
    remove_word_from_view(session, user_id, word)
    inform_user_of_word_change(message, 'remove', word)


def handle_word_in_user_db(session, word_in_user_db, message):
    """Handles the case when a word is in the user's database."""
    delete_word_from_db(session, word_in_user_db)
    inform_user_of_word_change(message, 'delete', word_in_user_db.word)


def handle_delete_word_request(message: types.Message) -> None:
    """Handles the request to delete a word from the user's word list."""
    session = SESSION
    user_id = get_user_id(session, message)
    word = message.text.lower()

    word_in_user_db = get_word_by_user_id(session, word, user_id)
    if word_in_user_db is None:
        handle_word_not_in_user_db(session, user_id, word, message)
    else:
        handle_word_in_user_db(session, word_in_user_db, message)

    session.close()
    show_interaction_menu(message, CHATBOT_BTNS, ['next', 'add_word', 'delete_word'])
