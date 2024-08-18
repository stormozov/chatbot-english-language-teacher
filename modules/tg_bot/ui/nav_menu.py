from telebot import types
from modules.tg_bot.bot_init import bot


def show_interaction_menu(
        user_message: types.Message,
        button_labels: dict[str, str],
        operations: list[str]
) -> None:
    """Shows an interaction menu to the user.

    Parameters:
        user_message (types.Message): The message object from the user.
        button_labels (dict): A dictionary of button names
            and their corresponding labels.
        operations (list): A list of action names to associate with buttons.
    """
    markup = types.InlineKeyboardMarkup(row_width=2)

    for i in range(0, len(operations), 2):
        row = []
        for j in range(2):
            if i + j < len(operations):
                row.append(
                    types.InlineKeyboardButton(
                        text=button_labels[operations[i + j]],
                        callback_data=operations[i + j]
                    )
                )
        markup.add(*row)

    bot.send_message(
        user_message.chat.id, 'Выберите действие:', reply_markup=markup
    )
