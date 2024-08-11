from telebot import types
from modules.db.models import Word
from modules.tg_bot.bot_init import bot
from modules.tg_bot.bot_config import SESSION, CHATBOT_BTNS
from modules.tg_bot.db_operations import (get_user_id, get_word_obj, add_word_to_db, delete_word_from_db,
                                          inform_user_of_word_change, remove_word_from_view)
from modules.tg_bot.menu import show_interaction_menu


def handle_add_word_request(message: types.Message) -> None:
    """Handles the request to add a new word to the user's word list."""
    session = SESSION
    user_id = get_user_id(session, message)
    word, translation = message.text.split(', ')
    word = word.capitalize()
    word_obj = get_word_obj(session, word, user_id)
    session.close()

    if not word_obj:
        add_word_to_db(
            session, word, user_id,
            translation, message
        )
        inform_user_of_word_change(message, word, 'add')

    show_interaction_menu(message, CHATBOT_BTNS, ['next', 'add_word', 'delete_word'])


def handle_delete_word_request(message: types.Message) -> None:
    """Handles the request to delete a word from the user's word list."""
    session = SESSION
    user_id = get_user_id(session, message)
    word = message.text
    word_lower = word.lower()
    # Check whether the user's input is a word that is already in the database,
    # and whether the user is associated with that word.
    word_in_db = session.query(Word).filter_by(user_id=user_id).filter(Word.word.ilike(f'%{word_lower}%')).first()
    session.close()

    if word_in_db is None:
        # Hide a word from a user if it is shared by all other users
        remove_word_from_view(session, user_id, word)
        inform_user_of_word_change(message, word, 'remove')
    else:
        # Word exists, delete it from the database
        delete_word_from_db(session, word_in_db)
        inform_user_of_word_change(message, word, 'delete')

    show_interaction_menu(message, CHATBOT_BTNS, ['next', 'add_word', 'delete_word'])
