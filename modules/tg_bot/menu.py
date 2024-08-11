import random
from telebot import types
from modules.tg_bot.bot_init import bot


def show_interaction_menu(message: types.Message, buttons: dict, actions: list) -> None:
    """
    Renders an interaction menu for the user with the provided buttons and actions.

    Parameters:
        message (types.Message): The message object from the user.
        buttons (dict): A dictionary of button names and their corresponding labels.
        actions (list): A list of action names to associate with buttons.
    """
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*[types.KeyboardButton(buttons[btn]) for btn in actions])

    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def show_one_item_menu(message: types.Message, button, send_text) -> None:
    """
    Sends a menu with a single item to the user.

    Parameters:
        message (types.Message): The message object from the user.
        button (str): The text of the button to display in the menu.
        send_text (str): The text to send to the user along with the menu.
    """
    bot.send_message(
        message.chat.id,
        send_text,
        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(button))
    )


def show_word_variant_menu(word_list: list, target_word) -> (types.ReplyKeyboardMarkup, int):
    """
    Generate answer choices for a quiz based on the user's text input.

    Parameters:
        word_list (list): A list of words to choose from.
        target_word: The word to be quizzed on.

    Returns:
        tuple: A tuple containing the keyboard markup and the ID of the word.
    """
    # Generate answer options
    other_words = [option.word for option in word_list if option.word != target_word.word]
    answer_options = random.sample(other_words, min(3, len(other_words)))
    answer_options.insert(random.randint(0, len(answer_options)), target_word.word)

    # Create the keyboard layout
    keyboard_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard_markup.add(*[types.KeyboardButton(option) for option in answer_options])

    return keyboard_markup, target_word.id
