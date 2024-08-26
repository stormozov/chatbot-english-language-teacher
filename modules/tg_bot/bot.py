from telebot import types

from modules.tg_bot.bot_config import (
    CHATBOT_BTNS, CHATBOT_COMMANDS, CHATBOT_MESSAGE
)
from modules.tg_bot.bot_init import bot
from modules.tg_bot.db.user_db_utils import handle_new_user
from modules.tg_bot.quiz.handle_quiz import handle_quiz
from modules.tg_bot.ui.drop_down_menu import menu_btn_commands
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

    handle_new_user(message)
    menu_btn_commands()


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call: types.CallbackQuery) -> None:
    """Handles the callback query from the bot."""
    if call.data in ('test_knowledge', 'next'):
        handle_quiz(call.message)
    elif call.data == 'add_word':
        handle_add_word(call.message)
    elif call.data == 'delete_word':
        handle_delete_word(call.message)
    elif call.data == 'about':
        handle_delete_word(call.message)
    elif call.data == 'help':
        handle_delete_word(call.message)


@bot.message_handler(commands=['help'])
def help_message(message: types.Message) -> None:
    """Handles the /help command and sends the user a list of available commands

    Args:
        message (types.Message): The message containing the /help command.

    Returns:
        None
    """
    handle_new_user(message)
    commands_list = get_all_bot_commands()
    commands = convert_command_list_to_text(commands_list)
    bot.send_message(message.chat.id, "Доступные команды:\n" + commands)


def get_all_bot_commands() -> list:
    """Returns a list of all available bot commands."""
    return [
        f"{command['command']} - {command['description']}"
        for command in CHATBOT_COMMANDS.values()
    ]


def convert_command_list_to_text(commands: list) -> str:
    """Converts a bot command to its text representation."""
    return '\n'.join(commands)


@bot.message_handler(commands=['about'])
def about_bot_command(message: types.Message) -> None:
    """Handles the /about command and sends the user information about the bot.

    Args:
        message (types.Message): The message containing the /about command.

    Returns:
        None
    """
    handle_new_user(message)
    bot.send_message(message.chat.id, CHATBOT_MESSAGE['about'])


def start_bot() -> None:
    """Starts the bot's polling process.

    This function initiates the bot's main loop, where it continuously checks
    for incoming updates and messages.

    Returns:
        None
    """
    bot.polling()
