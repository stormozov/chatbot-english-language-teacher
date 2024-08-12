import re
from telebot import types
from modules.db.models import Word
from modules.tg_bot.bot_init import bot
from modules.tg_bot.bot_config import SESSION, CHATBOT_BTNS, CHATBOT_ERRORS
from modules.tg_bot.db_operations import (get_user_id, get_word_obj, add_word_to_db, delete_word_from_db,
                                          inform_user_of_word_change, remove_word_from_view, check_word_in_db)
from modules.tg_bot.menu import show_interaction_menu


def validate_user_input(message: types.Message) -> tuple:
    """Validates the user's input and returns the word and translation"""
    try:
        word, translation = message.text.split(', ')
        word = word.strip().capitalize()
        translation = translation.strip().capitalize()
        return word, translation
    except ValueError:
        bot.send_message(message.chat.id, CHATBOT_ERRORS['add_word_value'])
        return None, None


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
        bot.send_message(message.chat.id, CHATBOT_ERRORS['add_word_value'])
        return

    word_obj = get_word_obj(session, word, user_id)
    session.close()

    if not word_obj:
        add_word_to_db(session, word, user_id, translation, message)
        inform_user_of_word_change(message, word, 'add')

    show_interaction_menu(message, CHATBOT_BTNS, ['next', 'add_word', 'delete_word'])


def handle_delete_word_request(message: types.Message) -> None:
    """Handles the request to delete a word from the user's word list."""
    session = SESSION
    user_id = get_user_id(session, message)
    word = message.text.lower()

    word_in_user_db = session.query(Word).filter_by(user_id=user_id).filter(Word.word.ilike(f'%{word}%')).first()
    if word_in_user_db is None:
        is_word = check_word_in_db(session, word)
        if is_word is None:
            bot.send_message(message.chat.id, CHATBOT_ERRORS['word_not_found'])
            session.close()
            return
        # Hide a word from a user if it is shared by all other users
        remove_word_from_view(session, user_id, word)
        inform_user_of_word_change(message, word, 'remove')
    else:
        # Word exists, delete it from the database
        delete_word_from_db(session, word_in_user_db)
        inform_user_of_word_change(message, word, 'delete')

    session.close()
    show_interaction_menu(message, CHATBOT_BTNS, ['next', 'add_word', 'delete_word'])
