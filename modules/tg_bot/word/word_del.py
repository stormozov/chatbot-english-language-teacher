from telebot import types

from ...db.models import Word
from ..bot_config import (
    CHATBOT_BTNS, CHATBOT_ERRORS, CHATBOT_MESSAGE, SESSION
)
from ..bot_init import bot
from ..db import (
    get_word_by_user_id,
    word_exists_in_db,
    handle_new_user,
    get_user_id,
    delete_word_from_db,
    remove_word_from_view
)
from ..response_handlers import inform_user_of_word_change
from ..ui import show_interaction_menu


@bot.message_handler(commands=['delete_word'])
def handle_delete_word(user_message: types.Message) -> None:
    """Handles the command to delete a word from the user's word list.

    Sends a message to the user to confirm the deletion and registers the
    next step handler to process the delete word request.
    """
    handle_new_user(user_message)
    bot.send_message(user_message.chat.id, CHATBOT_MESSAGE['delete_user_word'])
    bot.register_next_step_handler(user_message, handle_delete_word_request)


def handle_delete_word_request(user_message: types.Message) -> None:
    """Handles the request to delete a word from the user's word list.

    Deletes a word from the user's word list based on the user's input.
    """
    with SESSION as session:
        user_id: int = get_user_id(session, user_message)
        word_to_delete: str = user_message.text.title()

        word_in_user_db: Word = get_word_by_user_id(
            session,
            word_to_delete,
            user_id
        )
        if word_in_user_db is None:
            handle_word_not_in_user_db(
                session, user_id,
                word_to_delete, user_message
            )
        else:
            handle_word_in_user_db(
                session,
                word_in_user_db,
                user_message
            )

        show_interaction_menu(
            user_message,
            CHATBOT_BTNS,
            ['next', 'add_word', 'delete_word']
            )


def handle_word_not_in_user_db(
        session: SESSION,
        user_id: int,
        word: str,
        user_message: types.Message
) -> None:
    """Handles the case when a word is not in the user's database."""
    if not word_exists_in_db(session, word):
        bot.send_message(user_message.chat.id, CHATBOT_ERRORS['word_not_found'])
        return

    remove_word_from_view(session, user_id, word)
    inform_user_of_word_change(
        user_message, 'remove', word
    )


def handle_word_in_user_db(
        session: SESSION,
        word_in_user_db: Word,
        user_message: types.Message
) -> None:
    """Handles the case when a word is in the user's database."""
    delete_word_from_db(session, word_in_user_db)
    inform_user_of_word_change(
        user_message, 'delete', word_in_user_db.word
    )
