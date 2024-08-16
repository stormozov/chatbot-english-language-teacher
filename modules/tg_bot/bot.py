from telebot import types

from modules.tg_bot.bot_config import CHATBOT_BTNS, CHATBOT_MESSAGE, SESSION
from modules.tg_bot.bot_init import bot
from modules.tg_bot.db.user_db_utils import add_new_user, check_user_in_db
from modules.tg_bot.quiz.handle_quiz import handle_quiz
from modules.tg_bot.ui.nav_menu import show_interaction_menu
from modules.tg_bot.word.word_add import handle_add_word
from modules.tg_bot.word.word_del import handle_delete_word


@bot.message_handler(commands=['start'])
def start_message(message: types.Message) -> None:
    """ Start message handler """
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['start_message'])
    show_interaction_menu(
        message,
        CHATBOT_BTNS,
        ['test_knowledge', 'add_word', 'delete_word']
        )

    # Check if the user is already in the database
    with SESSION as session:
        handle_new_user(session, message)


def handle_new_user(session: SESSION, message: types.Message) -> None:
    """Handles the case when a new user is added to the database."""
    try:
        with (session.begin()):
            check_user_in_db(session, message) or \
             add_new_user(session, message)
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


def start_bot() -> None:
    """Starts the bot's polling process.

    This function initiates the bot's main loop, where it continuously checks
    for incoming updates and messages.

    Returns:
        None
    """
    bot.polling()
