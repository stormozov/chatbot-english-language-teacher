import telebot

from modules.tg_bot.bot_config import CHATBOT_COMMANDS
from modules.tg_bot.bot_init import bot


def convert_json_to_list() -> list[telebot.types.BotCommand]:
    """Converts the CHATBOT_COMMANDS JSON data into a list of BotCommand objects

    Returns:
        list[telebot.types.BotCommand]: A list of BotCommand objects,
    where each object contains a command key and its corresponding description.
    """
    return [
        telebot.types.BotCommand(
            key, CHATBOT_COMMANDS[key]['description']
        )
        for key in CHATBOT_COMMANDS.keys()
    ]


def menu_btn_commands() -> None:
    """Sets the bot's menu buttons"""
    commands = convert_json_to_list()
    bot.set_my_commands(commands)
