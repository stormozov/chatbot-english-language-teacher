from telebot import types

from modules.tg_bot.bot_config import (
    SESSION, CHATBOT_MESSAGE, CHATBOT_BTNS, CHATBOT_REGEX
)
from modules.tg_bot.bot_init import bot
from modules.tg_bot.db.word_db_crud import add_word_to_db
from modules.tg_bot.db.word_db_utils import get_word_by_user_id
from modules.tg_bot.db.user_db_utils import get_user_id, handle_new_user
from modules.tg_bot.response_handlers import inform_user_of_word_change
from modules.tg_bot.ui.nav_menu import show_interaction_menu
from modules.tg_bot.word.input_validation import validate_user_input
from modules.tg_bot.word.word_format import check_word_format


@bot.message_handler(commands=['add_word'])
def handle_add_word(user_message: types.Message) -> None:
    """Handles the command to add a word.

    Sends a message to the chat with the prompt to add a user word and
    registers the next step handler to process the request.
    """
    handle_new_user(user_message)
    bot.send_message(user_message.chat.id, CHATBOT_MESSAGE['add_user_word'])
    bot.register_next_step_handler(user_message, handle_add_word_request)


def handle_add_word_request(user_message: types.Message) -> None:
    """Handles the request to add a new word to the user's word list."""
    with SESSION as session:
        user_id: int = get_user_id(session, user_message)
        word, translation = validate_user_input(user_message)

        if not word or not translation:
            return

        if not check_word_format(
                CHATBOT_REGEX['eng'],
                CHATBOT_REGEX['rus'],
                word,
                translation
        ):
            inform_user_of_word_change(
                user_message, 'add_word_value'
            )
            return

        word_obj = get_word_by_user_id(session, word, user_id)

        if not word_obj:
            add_word_to_db(
                session,
                word,
                translation,
                user_id,
                user_message
            )
            inform_user_of_word_change(
                user_message, 'add', word
            )

        show_interaction_menu(
            user_message,
            CHATBOT_BTNS,
            ['next', 'add_word', 'delete_word']
            )
