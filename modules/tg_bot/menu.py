import random
from telebot import types
from modules.db.models import Word
from modules.tg_bot.bot_init import bot


def show_interaction_menu(message: types.Message, button_labels: dict[str, str], action_callbacks: list[str]) -> None:
    """
    Renders an interaction menu for the user with the provided buttons and actions.

    Parameters:
        message (types.Message): The message object from the user.
        button_labels (dict): A dictionary of button names and their corresponding labels.
        action_callbacks (list): A list of action names to associate with buttons.
    """
    markup = types.InlineKeyboardMarkup(row_width=2)

    for i in range(0, len(action_callbacks), 2):
        row = []
        for j in range(2):
            if i + j < len(action_callbacks):
                row.append(
                    types.InlineKeyboardButton(
                        text=button_labels[action_callbacks[i + j]],
                        callback_data=action_callbacks[i + j]
                    )
                )
        markup.add(*row)

    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


def show_word_variant_menu(word_list: list, target_word: Word) -> tuple[types.ReplyKeyboardMarkup, int]:
    """
    Generate answer choices for a quiz based on the user's text input.

    Parameters:
        word_list (list): A list of Word objects.
        target_word (Word): The target word to generate answer choices for.

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
