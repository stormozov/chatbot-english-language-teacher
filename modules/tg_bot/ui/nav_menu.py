from telebot import types
from modules.tg_bot.bot_init import bot


def create_inline_keyboard(row_width: int) -> types.InlineKeyboardMarkup:
    """Creates an inline keyboard with a specified row width.

    Args:
        row_width (int): The width of the keyboard rows.

    Returns:
        types.InlineKeyboardMarkup: The created keyboard.
    """
    return types.InlineKeyboardMarkup(row_width=row_width)


def create_buttons(button_labels: dict[str, str], operations: list[str]) \
        -> list[types.InlineKeyboardButton]:
    """Creates a list of inline keyboard buttons with labels and callback data.

    Args:
        button_labels (dict[str, str]): A dictionary of button labels.
        operations (list[str]): A list of button operations.

    Returns:
        list[types.InlineKeyboardButton]: The list of created buttons.
    """
    return [
        types.InlineKeyboardButton(text=button_labels[op], callback_data=op)
        for op in operations
    ]


def send_message_with_keyboard(
        user_message: types.Message,
        keyboard: types.InlineKeyboardMarkup,
        text: str
) -> None:
    """Sends a message with an inline keyboard.

    Args:
        user_message (types.Message): The user's message.
        keyboard (types.InlineKeyboardMarkup): The keyboard to send.
        text (str): The text to send.
    """
    bot.send_message(user_message.chat.id, text, reply_markup=keyboard)


def show_interaction_menu(
        user_message: types.Message,
        button_labels: dict[str, str],
        operations: list[str]
) -> None:
    """Shows an interaction menu with buttons.

    Args:
        user_message (types.Message): The user's message.
        button_labels (dict[str, str]): A dictionary of button labels.
        operations (list[str]): A list of button operations.
    """
    keyboard = create_inline_keyboard(2)
    buttons = create_buttons(button_labels, operations)
    keyboard.add(*buttons)
    send_message_with_keyboard(
        user_message, keyboard, 'Выберите действие:'
    )
