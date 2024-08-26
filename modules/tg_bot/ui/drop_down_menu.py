import telebot

from ..bot_config import CHATBOT_COMMANDS
from ..bot_init import bot


def convert_json_to_list() -> list[telebot.types.BotCommand]:
    """Converts the CHATBOT_COMMANDS JSON data into a list of BotCommand objects

    Returns:
        list[telebot.types.BotCommand]: A list of BotCommand objects,
    where each object contains a command key and its corresponding description.
    """
    return [
        telebot.types.BotCommand(
            value["command"], value["description"]
        )
        for value in CHATBOT_COMMANDS.values()
    ]


def menu_btn_commands() -> None:
    """Sets the bot's menu buttons"""
    commands = convert_json_to_list()
    bot.set_my_commands(commands)
