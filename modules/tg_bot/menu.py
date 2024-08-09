from telebot import types
from modules.tg_bot.bot_init import bot


def show_interaction_menu(message: types.Message, buttons: dict) -> None:
    """Send the main menu"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(buttons[btn]) for btn in ['next', 'add_word', 'delete_word']])

    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def show_one_item_menu(message: types.Message, button, send_text) -> None:
    """
        Sends a menu with a single item to the user.

        Parameters:
            message (types.Message): The message object from the user.
            button (str): The text of the button to display in the menu.
            send_text (str): The text to send to the user along with the menu.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(button))
    bot.send_message(message.chat.id, send_text, reply_markup=markup)


def show_word_variant_menu(message: types.Message, words: list, word, random) -> (types.ReplyKeyboardMarkup, int):
    """ Generate answer choices for a quiz based on the user's text input. """
    # Create a list of answer choices
    variants = [word.word]  # Английское слово
    # Add 3 random English words as distractors
    distractors = [w.word for w in words if w.word != word.word]
    random.shuffle(distractors)
    variants.extend(distractors[:3])
    random.shuffle(variants)
    word_id = word.id
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    row = []
    for variant in variants:
        item = types.KeyboardButton(variant)
        row.append(item)
        if len(row) == 2:
            markup.row(*row)
            row = []

    if row:
        markup.row(*row)

    return markup, word_id
