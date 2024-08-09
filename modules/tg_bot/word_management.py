from telebot import types
from modules.tg_bot.bot_init import bot
from modules.tg_bot.bot_config import SESSION, CHATBOT_BTNS
from modules.tg_bot.db_operations import (get_user_id, get_word_obj, add_word_to_db, delete_word_from_db,
                                          inform_user_of_word_change)
from modules.tg_bot.menu import show_interaction_menu


def handle_add_word_request(message: types.Message) -> None:
    """Handles the request to add a new word to the user's word list."""
    session = SESSION
    user_id = get_user_id(session, message)
    word, translation = message.text.split(', ')
    word_obj = get_word_obj(session, word, user_id)
    session.close()

    if not word_obj:
        add_word_to_db(
            session, word, user_id,
            translation, message
        )
        inform_user_of_word_change(message, word, 'add')

    show_interaction_menu(message, CHATBOT_BTNS)


def handle_delete_word_request(message: types.Message) -> None:
    """Handles the request to delete a word from the user's word list."""
    session = SESSION
    user_id = get_user_id(session, message)
    word = message.text
    word_obj = get_word_obj(session, word, user_id)
    session.close()

    if word_obj:
        delete_word_from_db(session, word_obj)
        inform_user_of_word_change(message, word, 'delete')
    else:
        bot.send_message(message.chat.id, f'Слово {word} не найдено в вашем словаре.')

    show_interaction_menu(message, CHATBOT_BTNS)
